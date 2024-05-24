import csv
import json
from collections import namedtuple
from pathlib import Path
from typing import Dict, List

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


def load_metadata(metadata_file_path: Path):
    data_dicts = []
    KeyTransform = namedtuple("KeyTransform", ["old_key", "new_key", "default_value"])

    with open(metadata_file_path) as raw_file:
        data_dicts = (
            list(csv.DictReader(raw_file))
            if metadata_file_path.suffix == ".csv"
            else [json.load(raw_file)]
        )

    for data_dict in data_dicts:
        if "project" in metadata_file_path.name:
            key_transforms = [KeyTransform._make(element) for element in PROJECT_METADATA_KEYS]
        elif "sample" in metadata_file_path.name:
            key_transforms = [KeyTransform._make(element) for element in SAMPLE_METADATA_KEYS]
        else:
            key_transforms = [KeyTransform._make(element) for element in LIBRARY_METADATA_KEYS]

        for element in key_transforms:
            if element.old_key in data_dict:
                data_dict[element.new_key] = data_dict.pop(element.old_key, element.default_value)

    return data_dicts


def write_metadata_dicts(list_of_dicts: List[Dict], output_file_path: str, **kwargs) -> None:
    """
    Writes a list of dictionaries to a csv-like file.
    Optional modifiers to the csv.DictWriter can be passed to function as kwargs.
    """
    kwargs["fieldnames"] = kwargs.get("fieldnames", utils.get_keys_from_dicts(list_of_dicts))
    kwargs["delimiter"] = kwargs.get("delimiter", common.TAB)

    with open(output_file_path, "w", newline="") as raw_file:
        csv_writer = csv.DictWriter(raw_file, **kwargs)
        csv_writer.writeheader()
        csv_writer.writerows(list_of_dicts)
