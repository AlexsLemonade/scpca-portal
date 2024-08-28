import logging
import shutil
from argparse import BooleanOptionalAction
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from scpca_portal import common, s3
from scpca_portal.models import Project
from scpca_portal.models.computed_file import ComputedFile

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

    @staticmethod
    def clean_up_input_data() -> None:
        shutil.rmtree(common.INPUT_DATA_PATH, ignore_errors=True)

    def create_computed_file(self, future, *, update_s3: bool, clean_up_output_data: bool) -> None:
        """
        Saves computed file returned from future to the db.
        Uploads file to s3 and cleans up output data depending on passed options.
        """
        if computed_file := future.result():

            # Only upload and clean up projects and the last sample if multiplexed
            if computed_file.project or computed_file.sample.is_last_multiplexed_sample:
                if update_s3:
                    s3.upload_output_file(computed_file.s3_key, computed_file.s3_bucket)
                if clean_up_output_data:
                    computed_file.clean_up_local_computed_file()
            computed_file.save()

        # Close DB connection for each thread.
        connection.close()

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
        project = Project.objects.get(scpca_id=scpca_project_id)
        # Purge all of a project's computed files (and optionally delete them from s3),
        # before generating new ones
        project.purge_computed_files(update_s3)

        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prepare data output directory.
        common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prep callback function
        on_get_file = partial(
            self.create_computed_file,
            update_s3=update_s3,
            clean_up_output_data=clean_up_output_data,
        )

        # Prepare a threading.Lock for each sample, with the chief purpose being to protect
        # multiplexed samples that share a zip file.
        locks = {}
        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            # Generated project computed files
            for config in common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS:
                tasks.submit(
                    ComputedFile.get_project_file,
                    project,
                    config,
                    project.get_download_config_file_output_name(config),
                ).add_done_callback(on_get_file)

            # Generated sample computed files
            for sample in project.samples.all():
                for config in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGURATIONS:
                    sample_lock = locks.setdefault(sample.get_config_identifier(config), Lock())
                    tasks.submit(
                        ComputedFile.get_sample_file,
                        sample,
                        config,
                        sample.get_download_config_file_output_name(config),
                        sample_lock,
                    ).add_done_callback(on_get_file)

        project.update_downloadable_sample_count()

        if clean_up_input_data:
            logger.info("Cleaning up input data")
            self.clean_up_input_data()
