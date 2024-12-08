import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Dict, List, Set

from django.conf import settings
from django.db import connection
from django.template.defaultfilters import pluralize

from scpca_portal import metadata_file, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import (
    ComputedFile,
    Contact,
    ExternalAccession,
    Project,
    Publication,
    Sample,
)

logger = get_and_configure_logger(__name__)


def prep_data_dirs(wipe_input_dir: bool = False, wipe_output_dir: bool = True) -> None:
    """
    Create the input and output data dirs, if they do not yet exist.
    Allow for options to be passed to wipe these dirs if they do exist.
        - wipe_input_dir defaults to False because we typically want to keep input data files
        between testing rounds to speed up our tests.
        - wipe_output_dir defaults to True because we typically don't want to keep around
        computed files after execution.
    The options are given to the caller for to customize behavior for different use cases.
    """
    # Prepare data input directory.
    if wipe_input_dir:
        shutil.rmtree(settings.INPUT_DATA_PATH, ignore_errors=True)
    settings.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

    # Prepare data output directory.
    if wipe_output_dir:
        shutil.rmtree(settings.OUTPUT_DATA_PATH, ignore_errors=True)
    settings.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)


def remove_project_input_files(project_id: str) -> None:
    """Remove the input files located at the project_id's input directory."""
    shutil.rmtree(settings.INPUT_DATA_PATH / project_id, ignore_errors=True)


def get_projects_metadata(
    input_bucket_name: str, filter_on_project_id: str = ""
) -> List[Dict[str, Any]]:
    """
    Download all metadata files from the passed input bucket,
    load the project metadata file and return project metadata dicts.
    """
    s3.download_input_metadata(input_bucket_name)
    projects_metadata = metadata_file.load_projects_metadata(
        filter_on_project_id=filter_on_project_id
    )
    return projects_metadata


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


def _create_computed_file(
    computed_file: ComputedFile, update_s3: bool, clean_up_output_data: bool
) -> None:
    """
    Save computed file returned from future to the db.
    Upload file to s3 and clean up output data depending on passed options.
    """
    if update_s3:
        s3.upload_output_file(computed_file.s3_key, computed_file.s3_bucket)
    if clean_up_output_data:
        computed_file.clean_up_local_computed_file()

    if computed_file.sample and computed_file.has_multiplexed_data:
        computed_files = computed_file.get_multiplexed_computed_files()
        ComputedFile.objects.bulk_create(computed_files)
    else:
        computed_file.save()


def _create_computed_file_callback(future, *, update_s3: bool, clean_up_output_data: bool) -> None:
    """
    Wrap computed file saving and uploading to s3 in a way that accommodates multiprocessing.
    """
    if computed_file := future.result():
        _create_computed_file(computed_file, update_s3, clean_up_output_data)

    # Close DB connection for each thread.
    connection.close()


def generate_computed_file(
    *,
    download_config: Dict,
    project: Project | None = None,
    sample: Sample | None = None,
    update_s3: bool = True,
) -> None:

    # Purge old computed file
    if old_computed_file := (project or sample).get_computed_file(download_config):
        old_computed_file.purge(update_s3)

    if project and (computed_file := ComputedFile.get_project_file(project, download_config)):
        _create_computed_file(computed_file, update_s3, clean_up_output_data=False)
    if sample and (computed_file := ComputedFile.get_sample_file(sample, download_config)):
        _create_computed_file(computed_file, update_s3, clean_up_output_data=False)
        sample.project.update_downloadable_sample_count()


def generate_computed_files(
    project: Project,
    max_workers: int,
    update_s3: bool,
    clean_up_output_data: bool,
) -> None:
    """
    Generate all computed files associated with the passed project,
    on both sample and project levels.
    """
    # Purge all of a project's associated computed file objects before generating new ones.
    project.purge_computed_files(update_s3)

    # Prep callback function
    on_get_file = partial(
        _create_computed_file_callback,
        update_s3=update_s3,
        clean_up_output_data=clean_up_output_data,
    )

    with ThreadPoolExecutor(max_workers=max_workers) as tasks:
        # Generated project computed files
        for download_config in project.valid_download_configs:
            tasks.submit(
                ComputedFile.get_project_file,
                project,
                download_config,
            ).add_done_callback(on_get_file)

        # Generated sample computed files
        for sample in project.samples_to_generate:
            for download_config in sample.valid_download_configs:
                tasks.submit(
                    ComputedFile.get_sample_file,
                    sample,
                    download_config,
                ).add_done_callback(on_get_file)

    project.update_downloadable_sample_count()
