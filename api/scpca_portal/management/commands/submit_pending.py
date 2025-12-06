from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Submits all pending jobs to AWS Batch for processing."""

    def handle(self, *args, **kwargs):
        self.submit_pending()

    def submit_pending(self):
        submitted_jobs, pending_jobs, failed_jobs = Job.submit_pending()

        if submitted_jobs:
            logger.info(f"{len(submitted_jobs)} jobs were submitted to AWS Batch.")
        else:
            logger.info("No jobs were submitted to AWS Batch")

        if pending_jobs:
            logger.info(f"{len(pending_jobs)} jobs were not submitted but are still pending.")
        if failed_jobs:
            logger.info(f"{len(failed_jobs)} jobs failed to submit.")
