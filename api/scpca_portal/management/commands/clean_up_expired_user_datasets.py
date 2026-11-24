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
    Mark already-expired datasets as EXPIRED and clean up the corresponding computed files.
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

        updated_datasets = []

        for dataset in datasets:
            if dataset.expiration_delta + buffer <= now:
                dataset.state = DatasetStates.EXPIRED
                updated_datasets.append(dataset)
                # Clean up the corresponding computed file
                if computed_file := dataset.computed_file:
                    computed_file.purge(delete_from_s3=True)

        if updated_datasets:
            UserDataset.objects.bulk_update(updated_datasets, ["state"])
            updated_count = len(updated_datasets)
            logger.info(f"Cleaned up {updated_count} dataset{pluralize(updated_count)}.")
        else:
            logger.info("No datasets to clean up.")
