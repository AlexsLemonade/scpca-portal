from datetime import datetime, timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize
from django.utils.timezone import make_aware

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetStates
from scpca_portal.models import UserDataset

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Mark already-expired datasets as expired, and clean up the corresponding computed files.
    NOTE: This is a housekeeping command, used specifically for datasets generated
    before tagging S3 objects.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        self.clean_up_expired_user_datasets()

    def clean_up_expired_user_datasets(self) -> None:
        datasets = UserDataset.objects.filter(state=DatasetStates.SUCCEEDED)

        if not datasets.exists():
            logger.info("No datasets to clean up.")
            return

        now = make_aware(datetime.now())
        updated_fields = set()
        updated_datasets = []

        for dataset in datasets:
            # Populate the timestamp
            if dataset.expires_at is None:
                dataset.expires_at = dataset.expiration_delta
                updated_fields.add("expires_at")
            # Clean up the legacy resources and mark as expired
            # 8-day expiration via S3 Lifecycle policy + 1 day
            if dataset.expiration_delta + timedelta(days=2) <= now:
                dataset.state = DatasetStates.EXPIRED
                updated_fields.add("state")
                if computed_file := dataset.computed_file:
                    computed_file.purge(delete_from_s3=True)

            updated_datasets.append(dataset)

        if updated_fields:
            UserDataset.objects.bulk_update(updated_datasets, list(updated_fields))

        if deleted_count := len(
            [dataset for dataset in updated_datasets if dataset.state == DatasetStates.EXPIRED]
        ):
            logger.info(f"Cleaned up {deleted_count} dataset{pluralize(deleted_count)}.")
        else:
            logger.info("No datasets to clean up.")
