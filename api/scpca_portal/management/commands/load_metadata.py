import logging
from argparse import BooleanOptionalAction
from typing import Set

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import common, loader

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


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
            default=settings.PRODUCTION,
        )
        parser.add_argument("--reload-existing", action="store_true", default=False)
        parser.add_argument("--scpca-project-id", type=str)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, type=bool, default=settings.UPDATE_S3_DATA
        )
        parser.add_argument(
            "--submitter-whitelist",
            type=self.comma_separated_set,
            default=common.SUBMITTER_WHITELIST,
        )

    def handle(self, *args, **kwargs):
        self.load_metadata(**kwargs)

    def comma_separated_set(self, raw_str: str) -> Set[str]:
        return set(raw_str.split(","))

    def load_metadata(
        self,
        input_bucket_name: str,
        clean_up_input_data: bool,
        reload_existing: bool,
        scpca_project_id: str,
        update_s3: bool,
        submitter_whitelist: Set[str],
        **kwargs,
    ) -> None:
        """Loads metadata from input metadata files on s3 and creates model objects in the db."""
        loader.prepare_data_dirs(clean_up_input_data)

        for project_metadata in loader.get_projects_metadata(input_bucket_name, scpca_project_id):
            # validates that a project can be added to the db, and if possible, creates the project
            if project := loader.create_project(
                project_metadata, submitter_whitelist, input_bucket_name, reload_existing, update_s3
            ):
                loader.bulk_create_project_relations(project_metadata, project)
                loader.create_samples_and_libraries(project)

            loader.prepare_data_dirs(clean_up_input_data, scpca_project_id)
