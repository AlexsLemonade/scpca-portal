import logging
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand

from scpca_portal import ccdl_datasets
from scpca_portal.models import Dataset, Job, Project

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Create all ccdl datasets and dispatch them as jobs to AWS Batch.
    """

    def add_arguments(self, parser):
        parser.add_argument("--ignore-hash", type=bool, default=False, action=BooleanOptionalAction)

    def handle(self, *args, **kwargs):
        self.create_ccdl_datasets(**kwargs)

    def attempt_dataset(
        self, ccdl_name, project_id: str | None = None, ignore_hash: bool = False
    ) -> bool:
        dataset, found = Dataset.get_or_find_ccdl_dataset(ccdl_name, project_id)
        if not found and not dataset.valid_ccdl_dataset:
            return False
        if found and dataset.is_hash_unchanged and not ignore_hash:
            return False
        dataset.save()

        job = Job.get_dataset_job(dataset)
        try:
            job.submit()
            logger.info(f"{dataset} job submitted successfully.")
        except Exception as error:
            logger.exception(error)
            job.save()

        return True

    def create_ccdl_datasets(self, **kwargs) -> None:
        for ccdl_name in ccdl_datasets.TYPES:
            # Project Datasets
            for project in Project.objects.all():
                self.attempt_dataset(ccdl_name, project.scpca_id)

            # Portal Wide datasets
            if ccdl_name in ccdl_datasets.PORTAL_TYPE_NAMES:
                self.attempt_dataset(ccdl_name)
