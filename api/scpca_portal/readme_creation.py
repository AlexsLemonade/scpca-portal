from typing import Dict

from django.template.loader import render_to_string

from scpca_portal import common, utils

OUTPUT_README_FILE_NAME = "README.md"

README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
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
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    readme_template_key_parts = [download_config["modality"], download_config["format"]]
    if project:
        if download_config["includes_merged"]:
            readme_template_key_parts.append("MERGED")
        if not download_config["excludes_multiplexed"]:
            readme_template_key_parts.append("MULTIPLEXED")
        if download_config["metadata_only"]:
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
