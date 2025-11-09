import logging

from django.core.management.base import BaseCommand

from scpca_portal.models import Job

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """Submits all pending jobs to AWS Batch for processing.
    """

    def handle(self, *args, **kwargs):
        self.submit_pending()

    def submit_pending(self):
        logger.info("Submitting pending jobs to AWS Batch...")
        submitted_jobs = Job.submit_pending()

        if submitted_jobs:
            logger.info("Successfully submitted jobs to AWS Batch!")
        else:
            logger.info("No jobs were submitted to AWS Batch")
