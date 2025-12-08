import logging
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.exceptions import DatasetError, JobError
from scpca_portal.models import Dataset, Job

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Create all ccdl datasets and dispatch them as jobs to AWS Batch.
    """

    def add_arguments(self, parser):
        ignore_hash_help_text = """
        By default, datasets are only processed if they are new or their hash has changed.
        Ignore hash forces reprocessing even when the hash has not changed.
        """
        parser.add_argument(
            "--ignore-hash",
            type=bool,
            default=False,
            action=BooleanOptionalAction,
            help=ignore_hash_help_text,
        )

    def handle(self, *args, **kwargs):
        self.create_ccdl_datasets(**kwargs)

    def create_ccdl_datasets(self, ignore_hash, **kwargs) -> None:
        created_datasets, updated_datasets = Dataset.create_or_update_ccdl_datasets(
            ignore_hash=ignore_hash
        )
        if created_datasets:
            created_count = len(created_datasets)
            logger.info(f"{created_count} dataset{pluralize(created_count)} created.")
        if updated_datasets:
            updated_count = len(updated_datasets)
            logger.info(f"{updated_count} existing dataset{pluralize(updated_count)} updated.")

        submitted_jobs = []
        dispatchable_datasets = created_datasets + updated_datasets
        for dataset in dispatchable_datasets:
            job = Job.get_dataset_job(dataset)
            try:
                job.submit()
                submitted_jobs.append(job)
            except (DatasetError, JobError):
                logger.info(f"{job.dataset} job (attempt {job.attempt}) is being requeued.")
                job.increment_attempt_or_fail()

        if submitted_jobs:
            submitted_count = len(submitted_jobs)
            logger.info(
                f"{submitted_count} job{pluralize(submitted_count)} submitted successfully."
            )
