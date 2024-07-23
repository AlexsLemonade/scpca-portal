from typing import Dict

from django.template.loader import render_to_string

from scpca_portal import common, utils

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = common.TEMPLATE_PATH / "readme"
<<<<<<< HEAD
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"
=======
TEMPLATE_PATHS = {
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": TEMPLATE_ROOT / "single_cell.md",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED": TEMPLATE_ROOT / "single_cell_merged.md",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED": TEMPLATE_ROOT / "metadata_only.md",
    "SINGLE_CELL_ANN_DATA": TEMPLATE_ROOT / "anndata.md",
    "SINGLE_CELL_ANN_DATA_MERGED": TEMPLATE_ROOT / "anndata_merged.md",
    "SPATIAL_SINGLE_CELL_EXPERIMENT": TEMPLATE_ROOT / "spatial.md",
    "METADATA_ONLY": TEMPLATE_ROOT / "metadata_only.md",
}
>>>>>>> fd428a8 (Merge dev updates into feature/portal-medatada-command (#807))


def get_file_contents(download_config: Dict, project) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    readme_template_key_parts = [download_config["modality"], download_config["format"]]
    if download_config in common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS:
        if download_config["includes_merged"]:
            readme_template_key_parts.append("MERGED")
        if not download_config["excludes_multiplexed"]:
            readme_template_key_parts.append("MULTIPLEXED")
        if download_config["metadata_only"]:
            readme_template_key_parts = ["METADATA_ONLY"]

<<<<<<< HEAD
    # For the contents section
    contents_template = f"{TEMPLATE_ROOT}/contents/{'_'.join(readme_template_key_parts)}.md"

    return render_to_string(
        TEMPLATE_FILE_PATH,
        context={
            "date": utils.get_today_string(),
            "download_config": download_config,
            "contents_template": contents_template,
            "projects": [project],
=======
    return render_to_string(
        TEMPLATE_PATHS["_".join(readme_template_key_parts)],
        context={
            "additional_terms": project.get_additional_terms(),
            "date": utils.get_today_string(),
            "project_accession": project.scpca_id,
            "project_url": project.url,
>>>>>>> fd428a8 (Merge dev updates into feature/portal-medatada-command (#807))
        },
    ).strip()
