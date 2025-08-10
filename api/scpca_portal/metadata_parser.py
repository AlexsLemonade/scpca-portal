import csv
import json
from typing import Dict, List

from django.conf import settings

from scpca_portal import common, utils
from scpca_portal.models.original_file import OriginalFile

PROJECT_METADATA_KEYS = [
    # Fields used in Project model object creation
    ("has_bulk", "has_bulk_rna_seq", False),
    ("has_CITE", "has_cite_seq_data", False),
    ("has_multiplex", "has_multiplexed_data", False),
    ("has_spatial", "has_spatial_data", False),
    ("PI", "human_readable_pi_name", None),
    ("submitter", "pi_name", None),
    ("project_title", "title", None),
    # Fields used in Contact model object creation
    ("contact_email", "email", None),
    ("contact_name", "name", None),
    # Fields used in ExternalAccession model object creation
    ("external_accession", "accession", None),
    ("external_accession_raw", "has_raw", False),
    ("external_accession_url", "accession_url", None),
    # Field used in Publication model object creation
    ("citation_doi", "doi", None),
]

PROJECT_METADATA_VALUES_TRANSFORMS = {"diagnoses": lambda d: sorted(d.split(";"))}

LIBRARY_METADATA_KEYS = [
    ("project_id", "scpca_project_id", None),
    ("sample_id", "scpca_sample_id", None),
    ("library_id", "scpca_library_id", None),
    # Field only included in Single cell (and Multiplexed) libraries
    ("filtered_cells", "filtered_cell_count", None),
]

BULK_METADATA_KEYS = [
    ("project_id", "scpca_project_id", None),
    ("sample_id", "scpca_sample_id", None),
    ("library_id", "scpca_library_id", None),
]


def get_projects_metadata_ids(*, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME) -> List[str]:
    """
    Opens the projects metadata file and returns a list of all project ids.

    """
    projects_metadata_file = OriginalFile.get_input_projects_metadata_file(bucket=bucket)

    with open(projects_metadata_file.local_file_path) as raw_file:
        projects_metadata = csv.DictReader(raw_file)
        return [row["scpca_project_id"] for row in projects_metadata]


def load_projects_metadata(
    filter_on_project_ids: List[str], *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
) -> List[Dict]:
    """
    Opens, loads and parses list of project metadata dicts.
    Transforms keys in data dicts to match associated model attributes.
    If an optional project id is passed, all projects are filtered out except for the one passed.
    """
    projects_metadata_file = OriginalFile.get_input_projects_metadata_file(bucket=bucket)
    with open(projects_metadata_file.local_file_path) as raw_file:
        projects_metadata = list(csv.DictReader(raw_file))

    for project_metadata in projects_metadata:
        utils.transform_keys(project_metadata, PROJECT_METADATA_KEYS)
        utils.transform_values(project_metadata, PROJECT_METADATA_VALUES_TRANSFORMS)

    if filter_on_project_ids:
        return [pm for pm in projects_metadata if pm["scpca_project_id"] in filter_on_project_ids]

    return projects_metadata


def load_samples_metadata(
    project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
) -> List[Dict]:
    """
    Opens, loads and parses list of samples metadata.
    Transforms keys in data dicts to match associated model attributes.
    """
    samples_metadata_file = OriginalFile.get_input_samples_metadata_file(project_id, bucket=bucket)
    with open(samples_metadata_file.local_file_path) as raw_file:
        return list(csv.DictReader(raw_file))


def load_libraries_metadata(
    project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
) -> List[Dict]:
    """
    Opens, loads and parses all of a project's libraries metadata.
    Transforms keys in data dicts to match associated model attributes.
    """
    library_metadata_files = OriginalFile.get_input_library_metadata_files(
        project_id, bucket=bucket
    )

    libraries_metadata = []
    for library_metadata_file in library_metadata_files:
        with open(library_metadata_file.local_file_path) as raw_file:
            libraries_metadata.append(
                utils.transform_keys(json.load(raw_file), LIBRARY_METADATA_KEYS)
            )

    return libraries_metadata


def load_bulk_metadata(
    project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
) -> List[Dict]:
    """
    Opens, loads and parses bulk metadata located at inputted metadata_file_path.
    Transforms keys in data dicts to match associated model attributes.
    """
    bulk_metadata_file = OriginalFile.get_input_project_bulk_metadata_file(
        project_id, bucket=bucket
    )
    with open(bulk_metadata_file.local_file_path) as raw_file:
        bulk_metadata_dicts = list(csv.DictReader(raw_file, delimiter=common.TAB))

    for bulk_metadata_dict in bulk_metadata_dicts:
        utils.transform_keys(bulk_metadata_dict, BULK_METADATA_KEYS)

    return bulk_metadata_dicts
