from argparse import ArgumentParser
from operator import itemgetter

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Library, Project, Sample
from scpca_portal.models.loadable_resource_abc import ModelOutputCounts

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync current state of Project, Sample and Library objects with the DB.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)
        parser.add_argument("--skip-existing-file-download", type=bool, default=False)

    def handle(self, *args, **kwargs) -> None:
        self.sync_models(**kwargs)

    def format_model_changes(self, model_name: str, model_output_counts: ModelOutputCounts) -> str:
        created, deleted, locked, unlocked, tainted = itemgetter(
            "created", "deleted", "locked", "unlocked", "tainted"
        )(model_output_counts)
        return (
            f"{model_name}: {created} created, {deleted} deleted, {locked} locked, "
            f"{tainted} locked resources tainted, "
            f"and {unlocked} locked resources unlocked and untouched."
        )

    def sync_models(self, bucket: str, skip_existing_file_download: bool, **kwargs) -> None:
        logger.info("Syncing models...")

        project_output_counts = Project.sync_model(
            bucket=bucket, skip_existing_file_download=skip_existing_file_download
        )
        sample_output_counts = Sample.sync_model(
            bucket=bucket, skip_existing_file_download=skip_existing_file_download
        )
        library_output_counts = Library.sync_model(
            bucket=bucket, skip_existing_file_download=skip_existing_file_download
        )

        logger.info("Models syncing complete.")
        logger.info(self.format_model_changes("Project", project_output_counts))
        logger.info(self.format_model_changes("Sample", sample_output_counts))
        logger.info(self.format_model_changes("Library", library_output_counts))
