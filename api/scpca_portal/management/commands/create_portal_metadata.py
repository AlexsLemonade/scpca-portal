from argparse import BooleanOptionalAction

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import common, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import ComputedFile, Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Creates a computed file and zip for portal-wide metadata.
    Saves generated computed file the db.
    Uploads file to s3 and cleans up output data depending on passed options.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean-up-output-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )
        parser.add_argument("--delete-from-s3", action=BooleanOptionalAction, default=False)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, default=settings.UPDATE_S3_DATA
        )
        parser.add_argument("--purge", action=BooleanOptionalAction, default=False)

    def handle(self, *args, **kwargs):
        if kwargs("purge", False):
            self.purge_computed_file(delete_from_s3=kwargs.get("delete_from_s3", False))
        self.create_portal_metadata(**kwargs)

    def create_portal_metadata(self, clean_up_output_data: bool, update_s3: bool, **kwargs):
        logger.info("Creating the portal-wide metadata computed file")
        computed_file = ComputedFile.get_portal_metadata_file(
            Project.objects.all(), common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG
        )

        if computed_file:
            logger.info("Saving the object to the database")
            computed_file.save()

            if update_s3:
                logger.info("Updating the zip file in S3")
                s3.upload_output_file(computed_file.s3_key, computed_file.s3_bucket)

            if clean_up_output_data:
                logger.info("Cleaning up the output directory")
                computed_file.clean_up_local_computed_file()

        return computed_file

    def purge_computed_file(self, delete_from_s3=False):
        logger.info("Purging the portal-wide metadata computed file")
        computed_file = ComputedFile.objects.filter(portal_metadata_only=True).first()

        if computed_file:
            if delete_from_s3:
                logger.info("Deleting the zip from S3")
                s3.delete_output_file(computed_file.s3_key)
            logger.info("Deleting the instance from the database")
            computed_file.delete()
        else:
            logger.info("No computed file to purge")
