import logging
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand

from scpca_portal.models import Job

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """Terminates all submitted, incomplete jobs on AWS Batch,
    and creates new retry jobs if the retry flag is passed.
    """

    def add_arguments(self, parser):
        parser.add_argument("--reason", type=str, default="Terminated submitted jobs")
        parser.add_argument("--retry", action=BooleanOptionalAction, type=bool, default=False)

    def handle(self, *args, **kwargs):
        self.terminate_batch_jobs(**kwargs)

    def terminate_batch_jobs(self, reason, retry: bool = False, **kwargs):
        logger.info("Terminating jobs on AWS Batch...")
        terminated_jobs = Job.terminate_submitted(reason)

        if retry:
            logger.info("Creating new retry jobs...")
            retry_jobs = Job.create_retry_jobs(terminated_jobs)

            if retry_jobs:
                logger.info("Successfully created new retry jobs.")
            else:
                logger.info("No retry jobs were created.")

        if terminated_jobs:
            logger.info("Successfully terminated jobs on AWS Batch!")
        else:
            logger.info("No jobs were terminated on AWS Batch.")
