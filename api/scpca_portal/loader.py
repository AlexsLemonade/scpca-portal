from typing import Any, Dict, List, Set

from django.conf import settings
from django.template.defaultfilters import pluralize

from scpca_portal import s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Contact, ExternalAccession, OriginalFile, Project, Publication

logger = get_and_configure_logger(__name__)


def download_projects_metadata() -> None:
    """Download the projects metadata file."""
    projects_metadata_file = OriginalFile.objects.filter(
        is_metadata=True, project_id__isnull=True
    ).first()

    s3.download_files([projects_metadata_file])


def download_projects_related_metadata(filter_on_project_ids: List[str]) -> None:
    """
    Download all metadata files associated with the project ids in the passed project id list.
    """
    filter_on_projects_files = OriginalFile.objects.filter(project_id__in=filter_on_project_ids)

    metadata_original_files = filter_on_projects_files.filter(is_metadata=True)
    bulk_original_files = filter_on_projects_files.filter(is_bulk=True)

    s3.download_files(metadata_original_files | bulk_original_files)


def _can_process_project(project_metadata: Dict[str, Any], submitter_whitelist: Set[str]) -> bool:
    """
    Validate that a project can be processed by assessing that:
    - Input files exist for the project
    - The project's pi is on the whitelist of acceptable submitters
    """
    project_path = settings.INPUT_DATA_PATH / project_metadata["scpca_project_id"]
    if project_path not in settings.INPUT_DATA_PATH.iterdir():
        logger.warning(
            f"Metadata found for {project_metadata['scpca_project_id']},"
            "but no s3 folder of that name exists."
        )
        return False

    if project_metadata["pi_name"] not in submitter_whitelist:
        logger.warning("Project submitter is not in the white list.")
        return False

    return True


def _can_purge_project(
    project: Project,
    *,
    reload_existing: bool = False,
) -> bool:
    """
    Check to see if the reload_existing flag was passed,
    indicating willingness for an existing project to be purged from the db.
    Existing projects must be purged before processing and re-adding them.
    Return boolean as success status.
    """
    # Projects can only be intentionally purged.
    # If the reload_existing flag is not set, then the project should not be procssed.
    if not reload_existing:
        logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
        return False

    return True


def create_project(
    project_metadata: Dict[str, Any],
    submitter_whitelist: Set[str],
    input_bucket_name: str,
    reload_existing: bool,
    update_s3: bool,
) -> Project | None:
    """
    Validate that a project can be processed, creates it, and return the newly created project.
    """
    if not _can_process_project(project_metadata, submitter_whitelist):
        return

    # If project exists and cannot be purged, then throw a warning
    project_id = project_metadata["scpca_project_id"]
    if project := Project.objects.filter(scpca_id=project_id).first():
        # If there's a problem purging an existing project, then don't process it
        if _can_purge_project(project, reload_existing=reload_existing):
            # Purge existing projects so they can be re-added.
            logger.info(f"Purging '{project}")
            project.purge(delete_from_s3=update_s3)
        else:
            return

    logger.info(f"Importing Project {project_metadata['scpca_project_id']} data")
    project = Project.get_from_dict(project_metadata)
    project.s3_input_bucket = input_bucket_name
    project.save()

    Contact.bulk_create_from_project_data(project_metadata, project)
    ExternalAccession.bulk_create_from_project_data(project_metadata, project)
    Publication.bulk_create_from_project_data(project_metadata, project)

    project.load_metadata()
    if samples_count := project.samples.count():
        logger.info(f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'")

    return project
