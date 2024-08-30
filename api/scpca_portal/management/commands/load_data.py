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

    The data should be contained in an S3 bucket called scpca-portal-inputs.

    The directory structure for this bucket should follow this pattern:
        /project_metadata.csv
        /SCPCP000001/libraries_metadata.csv
        /SCPCP000001/samples_metadata.csv
        /SCPCP000001/SCPCS000109/SCPCL000126_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000126_processed.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000126_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000127_processed.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000127_unfiltered.rds

    The files will be zipped up and stats will be calculated for them.

    If run locally the zipped ComputedFiles will be copied to the
    "scpca-local-data" bucket.

    If run in the cloud the zipped ComputedFiles files will be copied
    to a stack-specific S3 bucket."""

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
        parser.add_argument(
            "--clean-up-output-data",
            action=BooleanOptionalAction,
            type=bool,
            default=settings.PRODUCTION,
        )
        parser.add_argument("--max-workers", type=int, default=10)
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
        self.load_data(**kwargs)

    def comma_separated_set(self, raw_str: str) -> Set[str]:
        return set(raw_str.split(","))

    def load_data(
        self,
        input_bucket_name: str,
        clean_up_input_data: bool,
        clean_up_output_data: bool,
        max_workers: int,
        reload_existing: bool,
        scpca_project_id: str,
        update_s3: bool,
        submitter_whitelist: Set[str],
        **kwargs,
    ) -> None:
        """Loads data from S3. Creates projects and loads data for them."""
        loader.prep_data_dirs()

        # load metadata
        for project_metadata in loader.get_projects_metadata(input_bucket_name, scpca_project_id):
            # validates that a project can be added to the db, and if possible, creates the project
            if project := loader.create_project(
                project_metadata, submitter_whitelist, input_bucket_name, reload_existing, update_s3
            ):
                loader.bulk_create_project_relations(project_metadata, project)
                loader.create_samples_and_libraries(project)

                if clean_up_input_data:
                    logger.info(f"Cleaning up '{project}' input metadata files")
                    loader.remove_project_input_files(project.scpca_id)

        # generate computed files
        for project in loader.get_projects_for_computed_file_generation(update_s3):
            loader.generate_computed_files(project, max_workers, update_s3, clean_up_output_data)
            loader.update_project_aggregate_values(project)

            if clean_up_input_data:
                logger.info(f"Cleaning up '{project}' input metadata files")
                loader.remove_project_input_files(project.scpca_id)
