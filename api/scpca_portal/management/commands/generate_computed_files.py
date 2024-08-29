import logging
from argparse import BooleanOptionalAction

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import loader

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Data files should be contained in an S3 bucket called scpca-portal-inputs.

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
        parser.add_argument("--scpca-project-id", type=str)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, type=bool, default=settings.UPDATE_S3_DATA
        )

    def handle(self, *args, **kwargs):
        self.generate_computed_files(**kwargs)

    def generate_computed_files(
        self,
        clean_up_input_data: bool,
        clean_up_output_data: bool,
        max_workers: int,
        scpca_project_id: str,
        update_s3: bool,
        **kwargs,
    ) -> None:
        """Generates a project's computed files according predetermined download configurations"""
        loader.clean_up_data_dirs()

        project = loader.get_project_for_computed_file_generation(scpca_project_id, update_s3)

        loader.generate_computed_files(project, max_workers, clean_up_output_data, update_s3)

        loader.update_project_aggregate_values(project)

        # There is no need to clear up the input and output data dirs at the end of execution,
        # as Batch will trigger this automatically upon job completion.
        # Adding it here is for testing purposes, allowing us to clean up input data if desired.
        # Output data is deleted on a computed file level, after each file is created, it's deleted.
        if clean_up_input_data:
            loader.clean_up_data_dirs()
