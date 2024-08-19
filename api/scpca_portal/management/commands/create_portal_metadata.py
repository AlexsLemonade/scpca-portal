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

    @staticmethod
    def clean_up_output_data():
        """Cleans up the output data files after processing the computed file"""
        logger.info("Cleaning up output data")
        # This static method may not be required using buffers

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean-up-output-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )

    def handle(self, *args, **kwargs):
        self.create_portal_metadata(**kwargs)

    def create_portal_metadata(self, **kwargs):
        logger.info("Creating the portal-wide metadata computed file")
        computed_file = ComputedFile.get_portal_metadata_file(
            Project.objects.all(), common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG
        )

        if kwargs["clean_up_output_data"]:
            self.clean_up_output_data()

        return computed_file
