import logging
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand

from scpca_portal import ccdl_datasets
from scpca_portal.exceptions import DatasetError, JobError
from scpca_portal.models import Dataset, Job, Project

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
        ccdl_project_ids = list(Project.objects.values_list("scpca_id", flat=True))
        portal_wide_ccdl_project_id = None
        dataset_ccdl_project_ids = [*ccdl_project_ids, portal_wide_ccdl_project_id]

        for ccdl_name in ccdl_datasets.TYPES:
            for ccdl_project_id in dataset_ccdl_project_ids:
                dataset, found = Dataset.get_or_find_ccdl_dataset(ccdl_name, ccdl_project_id)
                if found:
                    dataset.data = dataset.get_ccdl_data()

                if not found and not dataset.is_valid_ccdl_dataset:
                    continue
                if found and dataset.is_hash_unchanged and not ignore_hash:
                    continue
                dataset.save()

                job = Job.get_dataset_job(dataset)
                try:
                    job.submit()
                    logger.info(f"{dataset} job submitted successfully.")
                except (DatasetError, JobError):
                    logger.info(f"{job.dataset} job (attempt {job.attempt}) is being requeued.")
                    job.increment_attempt_or_fail()
