from argparse import ArgumentParser

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Library, Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync Project, Sample and Library metadata files with the DB.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)
        parser.add_argument("--skip-existing-file-download", type=bool, default=False)

    def handle(self, *args, **kwargs) -> None:
        self.sync_metadata(**kwargs)

    def sync_metadata(self, **kwargs) -> None:
        logger.info("Syncing metadata...")

        synced_projects_count = Project.sync_metadata()
        synced_samples_count = Sample.sync_metadata()
        synced_libraries_count = Library.sync_metadata()

        logger.info("Metadata sync complete.")
        logger.info(
            f"Sync totals: {synced_projects_count} projects, {synced_samples_count} samples, "
            f"and {synced_libraries_count} libraries."
        )
