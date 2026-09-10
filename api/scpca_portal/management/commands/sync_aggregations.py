from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync aggregations for the Project and Sample models.
    """

    def handle(self, *args, **kwargs) -> None:
        self.sync_aggregations(**kwargs)

    def sync_aggregations(self, **kwargs) -> None:
        logger.info("Syncing aggregations...")

        aggregated_projects_count = Project.sync_aggregations()
        aggregated_samples_count = Sample.sync_aggregations()

        logger.info("Aggregation syncing complete.")
        logger.info(
            f"Aggregation totals: {aggregated_projects_count} projects "
            f"and {aggregated_samples_count} samples."
        )
