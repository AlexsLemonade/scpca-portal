from typing import Dict

from django.db.models import QuerySet
from django.template.loader import render_to_string

from scpca_portal import common, utils

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = common.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"


def get_file_contents(download_config: Dict, queryset: QuerySet) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    portal_metadata_only = download_config.get("portal_metadata_only", False)
    readme_template_key_parts = [download_config["modality"], download_config["format"]]

    if portal_metadata_only:
        readme_template_key_parts = ["METADATA_ONLY"]
    if download_config in common.GENERATED_PROJECT_DOWNLOAD_CONFIG:
        if download_config["includes_merged"]:
            readme_template_key_parts.append("MERGED")
        if not download_config["excludes_multiplexed"]:
            readme_template_key_parts.append("MULTIPLEXED")
        if download_config["metadata_only"]:
            readme_template_key_parts = ["METADATA_ONLY"]

    # For the contents section
    contents_template = f"{TEMPLATE_ROOT}/contents/{'_'.join(readme_template_key_parts)}.md"

    return render_to_string(
        TEMPLATE_FILE_PATH,
        context={
            "date": utils.get_today_string(),
            "download_config": download_config,
            "contents_template": contents_template,
            "projects": queryset if portal_metadata_only else [queryset],
        },
    ).strip()
