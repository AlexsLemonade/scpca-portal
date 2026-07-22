from typing import Any

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import UserDataset

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Ensure all processed datasets have expires_at timestamp, and mark datasets that have
    passed the 7-day expiration as expired to enable regeneration option on the Portal.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        self.expire_user_datasets()

    def expire_user_datasets(self) -> None:
        updated_count = UserDataset.mark_expired_datasets()

        if updated_count:
            logger.info(f"Marked {updated_count} dataset{pluralize(updated_count)} as expired.")
        else:
            logger.info("No datasets were expired.")
