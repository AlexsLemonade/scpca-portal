from typing import Any

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetStates
from scpca_portal.models import UserDataset

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Backfill the expires_at timestamp if it is missing.
    NOTE: This is a housekeeping command used specifically for datasets generated
    before tagging S3 objects.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        self.backfill_dataset_expires_at()

    def backfill_dataset_expires_at(self) -> None:
        datasets = UserDataset.objects.filter(state=DatasetStates.SUCCEEDED, expires_at=None)

        updated_datasets = []

        for dataset in datasets:
            dataset.expires_at = dataset.expiration_delta
            updated_datasets.append(dataset)

        if updated_datasets:
            UserDataset.objects.bulk_update(updated_datasets, ["expires_at"])
            updated_count = len(updated_datasets)
            logger.info(f"Backfilled {updated_count} dataset{pluralize(updated_count)}.")
        else:
            logger.info("No datasets to backfill.")
