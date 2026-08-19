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
    - Backfill expires_at timestamp if missing
    - Mark already-expired datasets as EXPIRED and clean up the corresponding computed files.
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
        buffer = timedelta(days=1)  # expires_at + 1 day

        backfilled_timestamps = []
        marked_expired = []

        for dataset in datasets:
            expires_at = dataset.expiration_delta

            # Backfill missing timestamps
            if dataset.expires_at is None:
                dataset.expires_at = expires_at
                backfilled_timestamps.append(dataset)

            # Mark expired dataset
            if expires_at + buffer <= now:
                dataset.state = DatasetStates.EXPIRED
                marked_expired.append(dataset)
                # Clean up the corresponding computed file
                if computed_file := dataset.computed_file:
                    computed_file.purge(delete_from_s3=True)

        if backfilled_timestamps:
            UserDataset.objects.bulk_update(backfilled_timestamps, ["expires_at"])

        if marked_expired:
            UserDataset.objects.bulk_update(marked_expired, ["state"])
            deleted_count = len(marked_expired)
            logger.info(f"Cleaned up {deleted_count} dataset{pluralize(deleted_count)}.")
        else:
            logger.info("No datasets to clean up.")
