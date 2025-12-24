from argparse import BooleanOptionalAction
from typing import Set

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import common, loader, lockfile, metadata_parser, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import OriginalFile, Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Populates the database with data.

    Metadata files should be contained in an S3 bucket called scpca-portal-inputs.

    The bucket's directory structure, as it pertains to metadata files, should follow this pattern:
        /project_metadata.csv
        /SCPCP000001/samples_metadata.csv
        /SCPCP000001/SCPCS000001/SCPCL000001_metadata.json
        /SCPCP000001/SCPCS000002/SCPCL000002_spatial/SCPCL000002_metadata.json
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-bucket-name", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME
        )
        parser.add_argument(
            "--clean-up-input-data",
            action=BooleanOptionalAction,
            type=bool,
            default=settings.CLEAN_UP_DATA,
        )
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, type=bool, default=settings.UPDATE_S3_DATA
        )
        parser.add_argument(
            "--submitter-whitelist",
            type=self.comma_separated_set,
            default=common.SUBMITTER_WHITELIST,
        )

        reload_existing_help_text = """
        Reload projects that have previously been loaded into the db.
        Without --reload-existing, only new projects will be processed.
        """
        parser.add_argument(
            "--reload-existing", action="store_true", default=False, help=reload_existing_help_text
        )

        reload_locked_help_text = """
        Only reload projects that were previously in the lockfile but have since been removed.
        """
        parser.add_argument(
            "--reload-locked", action="store_true", default=False, help=reload_locked_help_text
        )

        scpca_portal_id_help_text = "Reload an individual project."
        parser.add_argument("--scpca-project-id", type=str, help=scpca_portal_id_help_text)

    def handle(self, *args, **kwargs):
        self.load_metadata(**kwargs)

    def comma_separated_set(self, raw_str: str) -> Set[str]:
        return set(raw_str.split(","))

    def load_metadata(
        self,
        input_bucket_name: str,
        clean_up_input_data: bool,
        reload_existing: bool,
        reload_locked: bool,
        scpca_project_id: str,
        update_s3: bool,
        submitter_whitelist: Set[str],
        **kwargs,
    ) -> None:
        """Loads metadata from input metadata files on s3 and creates model objects in the db."""
        if not OriginalFile.objects.exists():
            raise Exception(
                "OriginalFile table is empty. Run 'sync_original_files' first to populate it."
            )

        utils.create_data_dirs()
        loader.download_projects_metadata()

        projects_metadata_ids = set(metadata_parser.get_projects_metadata_ids())
        locked_project_ids = set(lockfile.get_locked_project_ids())
        safe_project_ids = projects_metadata_ids - locked_project_ids

        filter_on_project_ids = list(safe_project_ids)
        if reload_locked:
            filter_on_project_ids = list(
                Project.objects.filter(scpca_id__in=safe_project_ids, is_locked=True).values_list(
                    "scpca_id", flat=True
                )
            )

        if scpca_project_id:
            if scpca_project_id in safe_project_ids:
                filter_on_project_ids = [scpca_project_id]
            else:
                logger.info(f"{scpca_project_id} is not available to reload.")
                return

        loader.download_projects_related_metadata(filter_on_project_ids)
        for project_metadata in metadata_parser.load_projects_metadata(filter_on_project_ids):
            # validate that a project can be added to the db,
            # then creates it, all its samples and libraries, and all other relations
            if project := loader.create_project(
                project_metadata, submitter_whitelist, input_bucket_name, reload_existing, update_s3
            ):
                if clean_up_input_data:
                    logger.info(f"Cleaning up '{project}' input files")
                    utils.remove_nested_data_dirs(project.scpca_id)
