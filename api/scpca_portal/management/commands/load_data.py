import logging
import shutil
from argparse import BooleanOptionalAction
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Set

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.template.defaultfilters import pluralize

from scpca_portal import common, metadata_file, s3
from scpca_portal.models import Contact, ExternalAccession, Project, Publication
from scpca_portal.models.computed_file import ComputedFile

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
            "--whitelist", type=self.comma_separated_set, default=common.SUBMITTER_WHITELIST
        )

    def handle(self, *args, **kwargs):
        self.load_data(**kwargs)

    def comma_separated_set(self, raw_str: str) -> Set[str]:
        return set(raw_str.split(","))

    def can_process_project(self, project_metadata: Dict[str, Any], whitelist: Set[str]) -> bool:
        """
        Validates that a project can be processed by assessing that:
        - Input files exist for the project
        - The project's pi is on the whitelist of acceptable submitters
        """
        project_path = common.INPUT_DATA_PATH / project_metadata["scpca_project_id"]
        if project_path not in common.INPUT_DATA_PATH.iterdir():
            logger.warning(
                f"Metadata found for {project_metadata['scpca_project_id']},"
                "but no s3 folder of that name exists."
            )
            return False

        if project_metadata["pi_name"] not in whitelist:
            logger.warning("Project submitter is not in the white list.")
            return False

        return True

    def purge_project(
        self,
        project: Project,
        *,
        reload_existing: bool = False,
        update_s3: bool = False,
    ) -> bool:
        """
        Purges existing projects from the db so that they can be re-added when they are processed.
        S3 is updated accordingly. Returns boolean as success status.
        """
        # Projects can only be intentionally purged.
        # If the reload_existing flag is not set, then the project should not be procssed.
        if not reload_existing:
            logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
            return False

        # Purge existing projects so they can be re-added.
        logger.info(f"Purging '{project}")
        project.purge(delete_from_s3=update_s3)
        return True

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

    @staticmethod
    def clean_up_input_data(project) -> None:
        shutil.rmtree(common.INPUT_DATA_PATH / project.scpca_id, ignore_errors=True)

    @staticmethod
    def clean_up_output_data() -> None:
        for path in Path(common.OUTPUT_DATA_PATH).glob("*"):
            path.unlink(missing_ok=True)

    def load_data(
        self,
        input_bucket_name,
        clean_up_input_data,
        clean_up_output_data,
        max_workers,
        reload_existing,
        scpca_project_id,
        update_s3,
        whitelist,
        **kwargs,
    ) -> None:
        """Loads data from S3. Creates projects and loads data for them."""
        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prepare data output directory.
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)
        common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        s3.download_input_metadata(input_bucket_name)

        projects_metadata = metadata_file.load_projects_metadata(
            Project.get_input_project_metadata_file_path(), scpca_project_id
        )
        for project_metadata in projects_metadata:
            if not self.can_process_project(project_metadata, whitelist):
                continue

            # If project exists and cannot be purged, then throw a warning
            project_id = project_metadata["scpca_project_id"]
            if project := Project.objects.filter(scpca_id=project_id).first():
                # If there's a problem purging an existing project, then don't process it
                if not self.purge_project(
                    project, reload_existing=reload_existing, update_s3=update_s3
                ):
                    continue

            logger.info(f"Importing Project {project_metadata['scpca_project_id']} data")
            project = Project.get_from_dict(project_metadata)
            project.s3_input_bucket = input_bucket_name
            project.save()

            Contact.bulk_create_from_project_data(project_metadata, project)
            ExternalAccession.bulk_create_from_project_data(project_metadata, project)
            Publication.bulk_create_from_project_data(project_metadata, project)

            project.load_metadata()
            if samples_count := project.samples.count():
                logger.info(
                    f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'"
                )

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
                logger.info(f"Cleaning up '{project}' input data")
                self.clean_up_input_data(project)

            if clean_up_output_data:
                logger.info("Cleaning up output directory")
                self.clean_up_output_data()
