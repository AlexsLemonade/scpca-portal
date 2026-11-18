from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import CCDLDataset, Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Deletes all CCDL datasets for the project with ScPCA ID `scpca_id`,
    including their computed files in the database and in S3.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--scpca-id",
            help="The ScPCA ID of the project whose CCDL datasets will be deleted.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--allow-existing-project",
            action="store_true",
            default=False,
            help=(
                "Delete the CCDL datasets even if the project still exists in the database. "
                "By default, only datasets for purged projects are deleted."
            ),
        )

    def handle(self, *args, **kwargs) -> None:
        self.purge_ccdl_datasets(**kwargs)

    def purge_ccdl_datasets(self, scpca_id: str, allow_existing_project: bool, **kwargs) -> None:
        if Project.objects.filter(scpca_id=scpca_id).exists() and not allow_existing_project:
            logger.error(
                f"Project {scpca_id} still exists. "
                "Pass --allow-existing-project to delete its CCDL datasets anyway."
            )
            return

        if purged_count := CCDLDataset.purge_project_datasets(scpca_id):
            logger.info(
                f"Purged {purged_count} CCDL dataset{pluralize(purged_count)} for {scpca_id}."
            )
        else:
            logger.info(f"No CCDL datasets found for {scpca_id}.")
