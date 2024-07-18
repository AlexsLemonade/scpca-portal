from typing import Dict

from django.template.loader import render_to_string

from scpca_portal import common, utils

OUTPUT_README_FILE_NAME = "README.md"

README_ANNDATA_FILE_NAME = "readme_anndata.md"
README_ANNDATA_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_FILE_NAME

README_ANNDATA_MERGED_FILE_NAME = "readme_anndata_merged.md"
README_ANNDATA_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_MERGED_FILE_NAME

README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

README_SINGLE_CELL_MERGED_FILE_NAME = "readme_single_cell_merged.md"
README_SINGLE_CELL_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_MERGED_FILE_NAME

README_METADATA_NAME = "readme_metadata_only.md"
README_METADATA_PATH = common.OUTPUT_DATA_PATH / README_METADATA_NAME

README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

README_SPATIAL_FILE_NAME = "readme_spatial.md"
README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
README_TEMPLATE_ANNDATA_MERGED_FILE_PATH = README_TEMPLATE_PATH / "anndata_merged.md"
README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
README_TEMPLATE_SINGLE_CELL_MERGED_FILE_PATH = README_TEMPLATE_PATH / "single_cell_merged.md"
README_TEMPLATE_METADATA_PATH = README_TEMPLATE_PATH / "metadata_only.md"
README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"


def get_readme_from_download_config(download_config: Dict):
    match download_config:
        case {"metadata_only": True}:
            return README_METADATA_PATH
        case {"excludes_multiplexed": False}:
            return README_MULTIPLEXED_FILE_PATH
        case {"format": "ANN_DATA", "includes_merged": True}:
            return README_ANNDATA_MERGED_FILE_PATH
        case {"modality": "SINGLE_CELL", "includes_merged": True}:
            return README_SINGLE_CELL_MERGED_FILE_PATH
        case {"format": "ANN_DATA"}:
            return README_ANNDATA_FILE_PATH
        case {"modality": "SINGLE_CELL"}:
            return README_SINGLE_CELL_FILE_PATH
        case {"modality": "SPATIAL"}:
            return README_SPATIAL_FILE_PATH


TEMPLATE_PATHS = {
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": README_TEMPLATE_PATH / "single_cell.md",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED": README_TEMPLATE_PATH / "single_cell_merged.md",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED": README_TEMPLATE_PATH / "metadata_only.md",
    "SINGLE_CELL_ANN_DATA": README_TEMPLATE_PATH / "anndata.md",
    "SINGLE_CELL_ANN_DATA_MERGED": README_TEMPLATE_PATH / "anndata_merged.md",
    "SPATIAL_SINGLE_CELL_EXPERIMENT": README_TEMPLATE_PATH / "spatial.md",
    "METADATA_ONLY": README_TEMPLATE_PATH / "metadata_only.md",
}


def create_readme_file(download_config: Dict, project=None, sample=None) -> str:
    readme_template_key_parts = [download_config["modality"], download_config["format"]]
    if download_config["includes_merged"]:
        readme_template_key_parts.append("MERGED")
    elif not download_config["excludes_multiplexed"]:
        readme_template_key_parts.append("MULTIPLEXED")
    elif download_config["metadata_only"]:
        readme_template_key_parts = ["METADATA_ONLY"]

    if sample:
        project = sample.project

    return render_to_string(
        TEMPLATE_PATHS["_".join(readme_template_key_parts)],
        context={
            "additional_terms": project.get_additional_terms(),
            "date": utils.get_today_string(),
            "project_accession": project.scpca_id,
            "project_url": project.url,
        },
    ).strip()
