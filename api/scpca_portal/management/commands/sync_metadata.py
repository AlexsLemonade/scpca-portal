from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Library, Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync Project, Sample and Library metadata files with the DB.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        # TODO: Uncomment these args and pass them through
        #   when PR #2056 (which refactors sync_metadata) is merged in.
        # parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)
        # parser.add_argument("--skip-existing-file-download", type=bool, default=False)
        pass

    def handle(self, *args, **kwargs) -> None:
        self.sync_metadata(**kwargs)

    def sync_metadata(self, **kwargs) -> None:
        logger.info("Syncing metadata...")

        Project.sync_metadata()
        Sample.sync_metadata()
        Library.sync_metadata()

        # TODO: Should the sync_metadata methods return anything that could be logged out here?
        # For example, how many Projects, Samples, and Libraries have been synced?

        logger.info("Metadata sync complete.")
