from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Dataset, Job

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Create all ccdl datasets and dispatch them as jobs to AWS Batch.
    """

    def add_arguments(self, parser):
        ignore_hash_help_text = """
        By default, datasets are only processed if they are new or their hash has changed.
        Ignore hash forces reprocessing even when the hash has not changed.
        """
        retry_failed_jobs_help_text = """
        Retry failed jobs adds the failed jobs to the retry queue.
        Queued jobs are picked up by the submit_pending command.
        By default, failed jobs are queued.
        """

        parser.add_argument(
            "--ignore-hash",
            type=bool,
            default=False,
            action=BooleanOptionalAction,
            help=ignore_hash_help_text,
        )
        parser.add_argument(
            "--retry-failed-jobs",
            type=bool,
            default=True,
            action=BooleanOptionalAction,
            help=retry_failed_jobs_help_text,
        )

    def handle(self, *args, **kwargs):
        self.create_ccdl_datasets(**kwargs)

    def create_ccdl_datasets(self, ignore_hash, retry_failed_jobs, **kwargs) -> None:
        created_datasets, updated_datasets = Dataset.create_or_update_ccdl_datasets(
            ignore_hash=ignore_hash
        )
        if created_datasets:
            created_count = len(created_datasets)
            logger.info(f"{created_count} dataset{pluralize(created_count)} created.")
        if updated_datasets:
            updated_count = len(updated_datasets)
            logger.info(f"{updated_count} existing dataset{pluralize(updated_count)} updated.")

        submitted_jobs, failed_jobs = Job.submit_ccdl_datasets(created_datasets + updated_datasets)
        if submitted_jobs:
            submitted_count = len(submitted_jobs)
            logger.info(
                f"{submitted_count} job{pluralize(submitted_count)} submitted successfully."
            )
        if failed_jobs:
            failed_count = len(failed_jobs)
            logger.info(
                f"{failed_count} job{pluralize(failed_count)} failed: "
                ", ".join([str(failed_job) for failed_job in failed_jobs])
            )
            if retry_failed_jobs:
                for failed_job in failed_jobs:
                    failed_job.increment_attempt_or_fail()
                logger.info("Failed jobs added to retry queue.")
