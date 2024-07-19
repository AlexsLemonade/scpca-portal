import csv
import json
from collections import namedtuple
from pathlib import Path
from typing import Dict, List, Tuple

from scpca_portal import common, utils

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

SAMPLE_METADATA_KEYS = [
    ("age", "age_at_diagnosis", None),
]

LIBRARY_METADATA_KEYS = [
    ("library_id", "scpca_library_id", None),
    ("sample_id", "scpca_sample_id", None),
    # Field only included in Single cell (and Multiplexed) libraries
    ("filtered_cells", "filtered_cell_count", None),
]
KeyTransform = namedtuple("KeyTransform", ["old_key", "new_key", "default_value"])


def load_projects_metadata(metadata_file_path: Path):
    """
    Opens, loads and parses list of project metadata located at inputted metadata_file_path.
    Transforms keys in data dicts to match associated model attributes.
    """
    with open(metadata_file_path) as raw_file:
        data_dicts = list(csv.DictReader(raw_file))

    for data_dict in data_dicts:
        transform_keys(data_dict, PROJECT_METADATA_KEYS)

    return data_dicts


def load_samples_metadata(metadata_file_path: Path):
    """
    Opens, loads and parses list of sample metadata located at inputted metadata_file_path.
    Transforms keys in data dicts to match associated model attributes.
    """
    with open(metadata_file_path) as raw_file:
        data_dicts = list(csv.DictReader(raw_file))

    for data_dict in data_dicts:
        transform_keys(data_dict, SAMPLE_METADATA_KEYS)

    return data_dicts


def load_library_metadata(metadata_file_path: Path):
    """
    Opens, loads and parses single library's metadata located at inputted metadata_file_path.
    Transforms keys in data dicts to match associated model attributes.
    """
    with open(metadata_file_path) as raw_file:
        return transform_keys(json.load(raw_file), LIBRARY_METADATA_KEYS)


def transform_keys(data_dict: Dict, key_transforms: List[Tuple]):
    """
    Transforms keys in inputted data dict according to inputted key transforms tuple list.
    """
    for element in [KeyTransform._make(element) for element in key_transforms]:
        if element.old_key in data_dict:
            data_dict[element.new_key] = data_dict.pop(element.old_key, element.default_value)

    return data_dict


class MetadataFilenames:
    SINGLE_CELL_METADATA_FILE_NAME = "single_cell_metadata.tsv"
    SPATIAL_METADATA_FILE_NAME = "spatial_metadata.tsv"
    METADATA_ONLY_FILE_NAME = "metadata.tsv"


def get_metadata_file_name(download_config: Dict) -> str:
    """Return metadata file name according to passed download_config."""
    output_file_constant = (
        f'{download_config["modality"]}_METADATA_FILE_NAME'
        if not download_config.get("metadata_only", False)
        else "METADATA_ONLY_FILE_NAME"
    )

    return getattr(MetadataFilenames, output_file_constant)


def write_metadata_dicts(list_of_dicts: List[Dict], output_file_path: str, **kwargs) -> None:
    """
    Writes a list of dictionaries to a csv-like file.
    Optional modifiers to the csv.DictWriter can be passed to function as kwargs.
    """
    kwargs["fieldnames"] = kwargs.get(
        "fieldnames", utils.get_sorted_field_names(utils.get_keys_from_dicts(list_of_dicts))
    )
    kwargs["delimiter"] = kwargs.get("delimiter", common.TAB)
    # By default fill missing values with "NA"
    kwargs["restval"] = kwargs.get("restval", common.NA)

    sorted_list_of_dicts = sorted(
        list_of_dicts,
        key=lambda k: (
            k[common.PROJECT_ID_KEY],
            k[common.SAMPLE_ID_KEY],
            k[common.LIBRARY_ID_KEY],
        ),
    )

    with open(output_file_path, "w", newline="") as raw_file:
        csv_writer = csv.DictWriter(raw_file, **kwargs)
        csv_writer.writeheader()
        csv_writer.writerows(sorted_list_of_dicts)
