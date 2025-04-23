from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Sync all local submitted jobs' states with
    their corresponding AWS Batch job statuses.
    """

    def handle(self, *args, **kwargs):
        self.sync_batch_jobs()

    def sync_batch_jobs(self):
        logger.info("Syncing job states with AWS Batch...")
        success = Job.bulk_sync_state()

        if success:
            logger.info("Successfully synced job states with AWS Batch!")
        else:
            logger.info("No job state changes detected during the sync")
