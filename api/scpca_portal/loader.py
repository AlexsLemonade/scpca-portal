import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock
from typing import Any, Dict, List, Set

from django.db import connection
from django.template.defaultfilters import pluralize

from scpca_portal import common, metadata_file, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Contact, ExternalAccession, Project, Publication
from scpca_portal.models.computed_file import ComputedFile

logger = get_and_configure_logger(__name__)


def prep_data_dirs(wipe_input_dir: bool = False, wipe_output_dir: bool = True) -> None:
    """
    Creates the input and output data dirs, if they do not yet exist.
    Allows for options to be passed to wipe these dirs if they exist.
        - wipe_input_dir defaults to False because we typically want to keep input data files
        between testing rounds to speak up our tests.
        - wipe_output_dir defaults to True because we typically don't want to keep around
        computed files after execution.
    The options are given to the caller for to customize behavior for different use cases.
    """
    # Prepare data input directory.
    if wipe_input_dir:
        shutil.rmtree(common.INPUT_DATA_PATH, ignore_errors=True)
    common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

    # Prepare data output directory.
    if wipe_output_dir:
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)
    common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)


def remove_project_input_files(project_id: str) -> None:
    shutil.rmtree(common.INPUT_DATA_PATH / project_id, ignore_errors=True)


def get_projects_metadata(
    input_bucket_name: str, filter_on_project_id: str = ""
) -> List[Dict[str, Any]]:
    s3.download_input_metadata(input_bucket_name)
    projects_metadata = metadata_file.load_projects_metadata(
        filter_on_project_id=filter_on_project_id
    )
    return projects_metadata


def _can_process_project(project_metadata: Dict[str, Any], submitter_whitelist: Set[str]) -> bool:
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


def _can_purge_project(
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


def create_project(
    project_metadata: Dict[str, Any],
    submitter_whitelist: Set[str],
    input_bucket_name: str,
    reload_existing: bool,
    update_s3: bool,
) -> Project | None:
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

    return project


def bulk_create_project_relations(project_metadata: Dict[str, Any], project: Project) -> None:
    Contact.bulk_create_from_project_data(project_metadata, project)
    ExternalAccession.bulk_create_from_project_data(project_metadata, project)
    Publication.bulk_create_from_project_data(project_metadata, project)


def create_samples_and_libraries(project: Project) -> None:
    project.load_metadata()
    if samples_count := project.samples.count():
        logger.info(f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'")


def _prep_project_for_computed_file_generation(
    project: Project, update_s3: bool = False
) -> Project:
    """
    Purge all of a project's computed files (and optionally delete them from s3),
    before new ones are generated.
    """
    project.purge_computed_files(update_s3)
    return project


def get_project_for_computed_file_generation(
    project_id: str = "", update_s3: bool = False
) -> Project:
    """Retrieve, prep and return project for computed file generation."""
    return _prep_project_for_computed_file_generation(
        Project.objects.filter(scpca_id=project_id), update_s3
    )


def get_projects_for_computed_file_generation(update_s3: bool = False) -> List[Project]:
    """
    Query the database, prep and return all projects that need computed files to be generated.
    """
    return [
        _prep_project_for_computed_file_generation(project, update_s3)
        for project in Project.objects.filter(project_computed_files__isnull=True)
    ]


def _create_computed_file(future, *, update_s3: bool, clean_up_output_data: bool) -> None:
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
    project: Project,
    max_workers: int,
    update_s3: bool,
    clean_up_output_data: bool,
) -> None:
    # Prep callback function
    on_get_file = partial(
        _create_computed_file,
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


def update_project_aggregate_values(project: Project) -> None:
    project.update_downloadable_sample_count()
