from collections import namedtuple
from typing import Dict, List, Type

from django.apps import apps
from django.db import models

KeyTransform = namedtuple("KeyTransform", ["new_key", "old_key", "default_value"])


def project_data_transform() -> List[KeyTransform]:
    """
    Transforms keys in project data dictionary to match project (and associated) model attributes.
    """
    # Transforms for Project model object creation
    project_data_key_transforms = [
        ("has_bulk_rna_seq", "has_bulk", False),
        ("has_cite_seq_data", "has_CITE", False),
        ("has_multiplexed_data", "has_multiplex", False),
        ("has_spatial_data", "has_spatial", False),
        ("human_readable_pi_name", "PI", None),
        ("pi_name", "submitter", None),
        ("title", "project_title", None),
    ]

    # Transforms for Contact model object creation
    project_data_key_transforms.extend(
        [
            ("email", "contact_email", None),
            ("name", "contact_name", None),
        ]
    )

    # Transforms for ExternalAccession model object creation
    project_data_key_transforms.extend(
        [
            ("accession", "external_accession", None),
            ("has_raw", "external_accession_raw", False),
            ("accession_url", "external_accession_url", None),
        ]
    )

    # Transforms for Publication model object creation
    project_data_key_transforms.extend(
        [
            ("doi", "citation_doi", None),
        ]
    )

    return [KeyTransform._make(element) for element in project_data_key_transforms]


def sample_data_transform() -> Dict:
    """Transform keys in sample data dictionary to match sample model attributes"""
    sample_data_key_transforms = [("age_at_diagnosis", "age", None)]

    return [KeyTransform._make(element) for element in sample_data_key_transforms]


def library_data_transform(data: Dict) -> Dict:
    """Transform keys in library data dictionary to match sample model attributes"""
    library_data_key_transforms = [
        ("scpca_library_id", "library_id", None),
        ("scpca_sample_id", "sample_id", None),
    ]

    if "filtered_cells" in data:
        library_data_key_transforms.append(("filtered_cell_count", "filtered_cells", None))

    return [KeyTransform._make(element) for element in library_data_key_transforms]


def transform_keys(model: Type[models.Model], data_dict: Dict) -> Dict:
    key_transforms = []
    if model == apps.get_model("scpca_portal", "Project"):
        key_transforms = project_data_transform()
    elif model == apps.get_model("scpca_portal", "Sample"):
        key_transforms = (
            library_data_transform(data_dict)
            if "library_id" in data_dict
            else sample_data_transform()
        )

    for element in key_transforms:
        data_dict[element.new_key] = data_dict.pop(element.old_key, element.default_value)

    return data_dict
