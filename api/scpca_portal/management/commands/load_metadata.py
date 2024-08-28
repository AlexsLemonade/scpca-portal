import logging
import shutil
from argparse import BooleanOptionalAction
from typing import Any, Dict, Set

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal import common, metadata_file, s3
from scpca_portal.models import Contact, ExternalAccession, Project, Publication

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

    def can_process_project(
        self, project_metadata: Dict[str, Any], submitter_whitelist: Set[str]
    ) -> bool:
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

        if project_metadata["pi_name"] not in submitter_whitelist:
            logger.warning("Project submitter is not in the white list.")
            return False

        return True

    def can_purge_project(
        self,
        project: Project,
        *,
        reload_existing: bool = False,
    ) -> bool:
        """
        Checks to see if the reload_existing flag was passed,
        indicating willingness for an existing project to be purged from the db.
        Existing projects must be purged before processing and re-adding them.
        Returns boolean as success status.
        """
        # Projects can only be intentionally purged.
        # If the reload_existing flag is not set, then the project should not be procssed.
        if not reload_existing:
            logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
            return False

        return True

    @staticmethod
    def clean_up_input_data(project) -> None:
        shutil.rmtree(common.INPUT_DATA_PATH / project.scpca_id, ignore_errors=True)

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
        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        s3.download_input_metadata(input_bucket_name)

        projects_metadata = metadata_file.load_projects_metadata(
            filter_on_project_id=scpca_project_id
        )
        for project_metadata in projects_metadata:
            if not self.can_process_project(project_metadata, submitter_whitelist):
                continue

            # If project exists and cannot be purged, then throw a warning
            project_id = project_metadata["scpca_project_id"]
            if project := Project.objects.filter(scpca_id=project_id).first():
                # If there's a problem purging an existing project, then don't process it
                if self.can_purge_project(project, reload_existing=reload_existing):
                    # Purge existing projects so they can be re-added.
                    logger.info(f"Purging '{project}")
                    project.purge(delete_from_s3=update_s3)
                else:
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

            if clean_up_input_data:
                logger.info(f"Cleaning up '{project}' input data")
                self.clean_up_input_data(project)
