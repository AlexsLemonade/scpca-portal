import logging
from argparse import BooleanOptionalAction

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.processors import DatasetJobProcessor

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    This command is meant to be called as an entrypoint to a AWS Batch job instance.
    Individual files are computed according to their passed dataset.

    When computation is completed, files are uploaded to S3, and the job is marked as completed.

    At which point the instance which generated this computed file will receive a new job
    from the job queue and begin computing the next file.
    """

    def add_arguments(self, parser):
        parser.add_argument("--job-id", type=str)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, type=bool, default=settings.UPDATE_S3_DATA
        )

    def handle(self, *args, **kwargs):
        self.process_dataset(**kwargs)

    def process_dataset(self, job_id: str, update_s3: bool, **kwargs) -> None:
        processor = DatasetJobProcessor(job_id)
        processor.update_s3 = update_s3
        processor.run()
