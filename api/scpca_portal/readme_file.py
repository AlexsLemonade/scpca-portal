from typing import Dict

from django.db.models import QuerySet
from django.template.loader import render_to_string

from scpca_portal import common, utils

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = common.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"


# TODO: Temporarily edited until readme updates is finalized to prevent duplicate changes
# and test failures. Once the following PR is merged, all unique readme files per computed
# file are cleaned up and all the template contexts will be adjusted accordingly
# (currently still using old template contexts etc)
# https://github.com/AlexsLemonade/scpca-portal/pull/806
def get_file_contents(download_config: Dict, queryset: QuerySet) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    is_portal_metadata = any("portal_metadata_only" in key for key in download_config)
    common_download_config = (
        common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG
        if is_portal_metadata
        else common.GENERATED_PROJECT_DOWNLOAD_CONFIG
    )

    readme_template_key_parts = [download_config["modality"], download_config["format"]]
    if download_config in common_download_config:
        if download_config["includes_merged"]:
            readme_template_key_parts.append("MERGED")
        if not download_config["excludes_multiplexed"]:
            readme_template_key_parts.append("MULTIPLEXED")
        if download_config["metadata_only"]:
            readme_template_key_parts = ["METADATA_ONLY"]

    # Temporarily modified template contexts values here
    projects = queryset if is_portal_metadata else [queryset]
    # For the contents section
    contents_template = f"{TEMPLATE_ROOT}/contents/{'_'.join(readme_template_key_parts)}.md"

    return render_to_string(
        TEMPLATE_FILE_PATH,
        context={
            "date": utils.get_today_string(),
            "download_config": download_config,
            "contents_template": contents_template,
            "projects": projects,
        },
    ).strip()
