from typing import Dict


def project_data_transform(data: Dict) -> Dict:
    """
    Transforms keys in project data dictionary to match project (and associated) model attributes.
    """
    # Transforms for Project model object creation
    data["has_bulk_rna_seq"] = data.pop("has_bulk", False)
    data["has_cite_seq_data"] = data.pop("has_CITE", False)
    data["has_multiplexed_data"] = data.pop("has_multiplex", False)
    data["has_spatial_data"] = data.pop("has_spatial", False)
    data["human_readable_pi_name"] = data.pop("PI", None)
    data["pi_name"] = data.pop("submitter", None)
    data["title"] = data.pop("project_title", None)

    # Transforms for Contact model object creation
    data["email"] = data.pop("contact_email", None)
    data["name"] = data.pop("contact_name", None)

    # Transforms for ExternalAccession model object creation
    data["accession"] = data.pop("external_accession", None)
    data["has_raw"] = data.pop("external_accession_raw", False)
    data["accession_url"] = data.pop("external_accession_url", None)

    # Transforms for Publication model object creation
    data["doi"] = data.pop("citation_doi", None)

    return data


def sample_data_transform(data: Dict) -> Dict:
    """Transform keys in sample data dictionary to match sample model attributes"""
    data["age_at_diagnosis"] = data.pop("age")

    return data


def library_data_transform(data: Dict) -> Dict:
    """Transform keys in library data dictionary to match sample model attributes"""
    data["scpca_library_id"] = data.pop("library_id")
    data["scpca_sample_id"] = data.pop("sample_id")

    if "filtered_cells" in data:
        data["filtered_cell_count"] = data.pop("filtered_cells")

    return data
