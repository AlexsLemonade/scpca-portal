from collections import namedtuple
from typing import Dict, Type

from django.apps import apps
from django.db import models

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


def transform_keys(model: Type[models.Model], data_dict: Dict) -> Dict:
    key_transforms = []
    if model == apps.get_model("scpca_portal", "Project"):
        key_transforms = [KeyTransform._make(element) for element in PROJECT_METADATA_KEYS]
    elif model == apps.get_model("scpca_portal", "Sample"):
        key_transforms = (
            [KeyTransform._make(element) for element in LIBRARY_METADATA_KEYS]
            if "library_id" in data_dict
            else [KeyTransform._make(element) for element in SAMPLE_METADATA_KEYS]
        )

    for element in key_transforms:
        if element.old_key in data_dict:
            data_dict[element.new_key] = data_dict.pop(element.old_key, element.default_value)

    return data_dict
