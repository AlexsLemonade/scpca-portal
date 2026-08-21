from argparse import ArgumentParser

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Library, Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync current state of Project, Sample and Library objects with the DB.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)
        parser.add_argument("--skip-existing-file-download", type=bool, default=False)

    def handle(self, *args, **kwargs) -> None:
        self.sync_models(**kwargs)

    def sync_models(self, bucket: str, skip_existing_file_download: bool, **kwargs) -> None:
        logger.info("Syncing models...")

        Project.sync_model(bucket=bucket, skip_existing_file_download=skip_existing_file_download)
        Sample.sync_model(bucket=bucket, skip_existing_file_download=skip_existing_file_download)
        Library.sync_model(bucket=bucket, skip_existing_file_download=skip_existing_file_download)

        # TODO: Should the sync_model methods return anything that could be logged out here?
        # For example, how many Projects, Samples, and Libraries have been created and deleted?
        # Tainted/Locked/Unlocked as well?

        logger.info("Models syncing complete.")
