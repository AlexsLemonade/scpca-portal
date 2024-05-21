from typing import Dict


def project_data_transform(data: Dict) -> Dict:
    data["has_bulk_rna_seq"] = data.pop("has_bulk", False)
    data["has_cite_seq_data"] = data.pop("has_CITE", False)
    data["has_multiplexed_data"] = data.pop("has_multiplex", False)
    data["has_spatial_data"] = data.pop("has_spatial", False)
    data["human_readable_pi_name"] = data.pop("PI", None)
    data["pi_name"] = data.pop("submitter", None)
    data["title"] = data.pop("project_title", None)

    return data


def sample_data_transform(data: Dict) -> Dict:
    data["age_at_diagnosis"] = data.pop("age")

    return data


def library_data_transform(data: Dict) -> Dict:
    data["scpca_library_id"] = data.pop("library_id")
    data["scpca_sample_id"] = data.pop("sample_id")

    if "filtered_cells" in data:
        data["filtered_cell_count"] = data.pop("filtered_cells")

    return data
