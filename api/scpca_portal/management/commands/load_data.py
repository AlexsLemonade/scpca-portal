import logging
import shutil
from argparse import BooleanOptionalAction
from concurrent.futures import ThreadPoolExecutor
from operator import itemgetter
from pathlib import Path
from threading import Lock
from typing import Set

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.template.defaultfilters import pluralize

from scpca_portal import common, metadata_file, s3
from scpca_portal.models import Contact, ExternalAccession, Project, Publication
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.sample import Sample

ALLOWED_SUBMITTERS = {
    "christensen",
    "collins",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "mullighan",
    "murphy_chen",
    "pugh",
    "teachey_tan",
    "wu",
    "rokita",
}

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
        parser.add_argument("--input-bucket-name", type=str, default=common.INPUT_BUCKET_NAME)
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
        parser.add_argument("--reload-all", action="store_true", type=bool, default=False)
        parser.add_argument("--reload-existing", action="store_true", type=bool, default=False)
        parser.add_argument("--scpca-project-id", type=str)
        parser.add_argument("--skip-sync", action="store_true", type=bool, default=False)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, type=bool, default=settings.UPDATE_S3_DATA
        )

    def handle(self, *args, **kwargs):
        self.load_data(**kwargs)

    @staticmethod
    def project_has_s3_files(project_id: str) -> bool:
        return any(
            True
            for project_path in common.INPUT_DATA_PATH.iterdir()
            if project_path.name == project_id and project_path.is_dir()
            for nested_path in project_path.iterdir()
            if nested_path.is_dir()
        )

    def skip_project(
        self,
        metadata_project_id: str,
        passed_project_id: str,
        pi_name: str,
        allowed_submitters: Set,
    ):
        """
        Carries out a series of checks to determine whether or not a project should be processed.
        """
        # If project id was passed to command, verify that correct project is being processed
        if passed_project_id and passed_project_id != metadata_project_id:
            return True

        if not self.project_has_s3_files(metadata_project_id):
            logger.warning(
                f"Metadata found for '{metadata_project_id}', but no s3 folder of that name exists."
            )
            return True

        if pi_name not in allowed_submitters:
            logger.warning("Project submitter is not the white list.")
            return True

        return False

    def purge_project(
        self, project, reload_all: bool, reload_existing: bool, update_s3: bool
    ) -> bool:
        """
        Purges project if it exists in the database. Updates S3 accordingly.
        Returns boolean as success status.
        """
        # Purge existing projects so they can be re-added.
        if reload_all or reload_existing:
            logger.info(f"Purging '{project}")
            project.purge(delete_from_s3=update_s3)
            return True
        # Only import new projects.
        # If old ones are desired they should be purged and re-added.
        else:
            logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
            return False

    def create_computed_file(future, *, update_s3, clean_up_output_data):
        if computed_file := future.result():

            # Only upload and clean up projects and the last sample if multiplexed
            if computed_file.project or computed_file.sample.is_last_multiplexed_sample:
                if update_s3:
                    s3.upload_output_file(computed_file)
                if clean_up_output_data:
                    computed_file.clean_up_local_computed_file()
            computed_file.save()

        # Close DB connection for each thread.
        connection.close()

    @staticmethod
    def clean_up_input_data(project):
        shutil.rmtree(common.INPUT_DATA_PATH / project.scpca_id, ignore_errors=True)

    @staticmethod
    def clean_up_output_data():
        for path in Path(common.OUTPUT_DATA_PATH).glob("*"):
            path.unlink(missing_ok=True)

    def load_data(
        self,
        allowed_submitters: set[str] = ALLOWED_SUBMITTERS,
        input_bucket_name: str = common.INPUT_BUCKET_NAME,
        **kwargs,
    ):
        """Loads data from S3. Creates projects and loads data for them."""

        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prepare data output directory.
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)
        common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        s3.download_input_metadata()

        projects_metadata = metadata_file.load_projects_metadata(
            Project.get_input_project_metadata_file_path()
        )
        for project_metadata in projects_metadata:
            metadata_project_id = project_metadata["scpca_project_id"]
            passed_project_id = kwargs.get("scpca_project_id")

            pi_name = project_metadata["pi_name"]
            if self.skip_project(
                metadata_project_id, passed_project_id, pi_name, allowed_submitters
            ):
                continue

            if project := Project.objects.filter(scpca_id=metadata_project_id).first():
                get_purge_project_kwargs = itemgetter("reload_all", "reload_existing", "update_s3")
                # If there is a problem purging the project, then skip it
                if not self.purge_project(project, *get_purge_project_kwargs(kwargs)):
                    continue

            logger.info(f"Importing 'Project {metadata_project_id}' data")
            project = Project.get_from_dict(project_metadata)
            project.save()

            Contact.bulk_create_from_project_data(project_metadata, project)
            ExternalAccession.bulk_create_from_project_data(project_metadata, project)
            Publication.bulk_create_from_project_data(project_metadata, project)

            project.load_metadata()
            if samples_count := project.samples.count():
                logger.info(
                    f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'"
                )

            def on_get_file(future):
                if computed_file := future.result():

                    # Only upload and clean up projects and the last sample if multiplexed
                    if computed_file.project or computed_file.sample.is_last_multiplexed_sample:
                        if kwargs["update_s3"]:
                            s3.upload_output_file(computed_file)
                        if kwargs["clean_up_output_data"]:
                            computed_file.clean_up_local_computed_file()
                    computed_file.save()

                # Close DB connection for each thread.
                connection.close()

            samples = Sample.objects.filter(project__scpca_id=project.scpca_id)
            logger.info(
                f"Processing {len(samples)} sample{pluralize(len(samples))} using "
                f"{kwargs['max_workers']} worker{pluralize(kwargs['max_workers'])}"
            )

            # Prepare a threading.Lock for each sample, with the chief purpose being to protect
            # multiplexed samples that shares a zip file.
            locks = {}
            with ThreadPoolExecutor(max_workers=kwargs["max_workers"]) as tasks:
                # Generated project computed files
                for sample in samples:
                    for config in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGURATIONS:
                        sample_lock = locks.setdefault(sample.get_config_identifier(config), Lock())
                        tasks.submit(
                            ComputedFile.get_sample_file,
                            sample,
                            config,
                            sample.get_download_config_file_output_name(config),
                            sample_lock,
                        ).add_done_callback(on_get_file)

                # Generated project computed files
                for download_config in common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS:
                    tasks.submit(
                        ComputedFile.get_project_file,
                        project,
                        download_config,
                        project.get_download_config_file_output_name(download_config),
                    ).add_done_callback(on_get_file)

            project.update_downloadable_sample_count()

            if kwargs["clean_up_input_data"]:
                logger.info(f"Cleaning up '{project}' input data")
                self.clean_up_input_data(project)

            if kwargs["clean_up_output_data"]:
                logger.info("Cleaning up output directory")
                self.clean_up_output_data()
