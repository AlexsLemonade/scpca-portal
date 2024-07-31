import logging
from argparse import BooleanOptionalAction

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import common
from scpca_portal.models import ComputedFile, Project

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """Creates a computed file and zip for portal-wide metadata,
     saves the instance to the databse, and
     uploads the zip file to S3 bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean-up-output-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )

    def handle(self, *args, **kwargs):
        self.create_portal_metadata(**kwargs)

    def create_portal_metadata(self, **kwargs):
        clean_up_output_data = kwargs.get("clean_up_output_data", True)
        upload_s3 = kwargs.get("clean_up_output_data", False)

        logger.info("Creating the portal-wide metadata computed file")
        # TODO: Once the following PR is merged, the computed file will be saved correctly
        # (*currently it's not saved) https://github.com/AlexsLemonade/scpca-portal/pull/806
        computed_file = ComputedFile.get_portal_metadata_file(
            Project.objects.all(), common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG[0]
        )

        if computed_file:
            logger.info("Saving the computed file object to the database")
            computed_file.save()

            if upload_s3:
                logger.info("Uploading the zip file to S3")
                computed_file.upload_s3_file()

            if clean_up_output_data:
                logger.info("Cleaning up output directory")
                computed_file.clean_up_local_computed_file()

        return computed_file
