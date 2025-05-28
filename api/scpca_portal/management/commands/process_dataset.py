import logging
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand

from scpca_portal import loader, notifications
from scpca_portal.models import Dataset

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
        parser.add_argument("--dataset-id", type=str)
        parser.add_argument("--notify", type=bool, default=False, action=BooleanOptionalAction)

    def handle(self, *args, **kwargs):
        self.process_dataset(**kwargs)

    def process_dataset(self, dataset_id: str, notify: bool, **kwargs) -> None:
        loader.prep_data_dirs()

        dataset = Dataset.objects.filter(id=dataset_id).first()
        if not dataset:
            logger.error(f"{dataset} does not exist.")
        loader.process_dataset(dataset)

        if notify:
            notifications.send_dataset_file_completed_email(dataset_id)
