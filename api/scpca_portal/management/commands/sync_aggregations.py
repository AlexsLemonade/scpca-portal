from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync aggregations for the Project and Sample models.
    """

    def handle(self, *args, **kwargs) -> None:
        self.sync_metadata(**kwargs)

    def sync_metadata(self, **kwargs) -> None:
        logger.info("Syncing aggregations...")

        aggregated_projects_count = Project.sync_aggregations(
            Project.objects.filter(loaded_state=LoadableResourceStates.SYNCED)
        )
        aggregated_samples_count = Sample.sync_aggregations(
            Sample.objects.filter(loaded_state=LoadableResourceStates.SYNCED)
        )

        logger.info("Aggregation syncing complete.")
        logger.info(
            f"Aggregation totals: {aggregated_projects_count} projects "
            f"and {aggregated_samples_count} samples."
        )
