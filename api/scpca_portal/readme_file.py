from collections import namedtuple
from typing import Dict, Iterable

from django.conf import settings
from django.template.loader import render_to_string

from scpca_portal import common, utils  # ccdl_datasets,
from scpca_portal.enums import DatasetDataProjectConfig, DatasetFormats, Modalities

# from scpca_portal.enums import CCDLDatasetNames

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"

# Dataset Readme Templates
README_ROOT = settings.TEMPLATE_PATH / "dataset_readme"

# used in get_dataset_contents_section and in 2_contents.md
ContentRow = namedtuple("ContentRow", ["project", "modality", "format", "docs"])


def add_metadata_content_rows(content_rows: set, dataset) -> set:
    docs_link = "USER_METADATA_LINK"  # wont be accessible from the endpoint for now?

    if dataset.is_ccdl and not dataset.ccdl_project_id:
        docs_link = "PORTAL_METADATA_LINK"
    elif dataset.is_ccdl and dataset.ccdl_project_id:
        docs_link = "PROJECT_METADATA_LINK"

    for project in dataset.projects:
        content_rows.add(ContentRow(project, common.NA, common.NA, docs_link))

    return content_rows


def add_ann_data_content_rows(content_rows: set, dataset) -> set:
    # SINGLE_CELL
    for project in dataset.single_cell_projects:
        # ANN_DATA
        docs_link = "ANN_DATA"

        # HAS CITE-SEQ
        if project.has_cite_seq_data:
            docs_link = "ANN_DATA_WITH_CITE_SEQ"

        # ANN_DATA_MERGED
        if dataset.data[project.scpca_id].get(DatasetDataProjectConfig.MERGE_SINGLE_CELL):
            docs_link = "ANN_DATA_MERGED"
            # ANN_DATA_MERGED_WITH_CITE
            if project.has_cite_seq_data:
                docs_link = "ANN_DATA_MERGED_WITH_CITE-SEQ"

        content_rows.add(ContentRow(project, Modalities.SINGLE_CELL, dataset.format, docs_link))

    return content_rows


def add_single_cell_experiment_content_rows(content_rows: set, dataset) -> set:
    # SINGLE_CELL
    for project in dataset.single_cell_projects:
        # SINGLE_CELL_EXPERIMENT
        docs_link = "SINGLE_CELL_EXPERIMENT"

        # SINGLE_CELL_EXPERIMENT_MERGED
        if dataset.data[project.scpca_id].get(DatasetDataProjectConfig.MERGE_SINGLE_CELL):
            docs_link = "SINGLE_CELL_EXPERIMENT_MERGED"
        # SINGLE_CELL_EXPERIMENT_MULTIPLEXED
        elif (
            dataset.get_samples(project.scpca_id, Modalities.SINGLE_CELL)
            .filter(has_multiplexed_data=True)
            .exists()
        ):
            docs_link = "SINGLE_CELL_EXPERIMENT_MULTIPLEXED"

        content_rows.add(ContentRow(project, Modalities.SINGLE_CELL, dataset.format, docs_link))

    return content_rows


def get_dataset_contents_section(dataset):
    # Metadata

    content_rows = set()

    # These rows depend on the format
    if dataset.format == DatasetFormats.METADATA:
        content_rows = add_metadata_content_rows(content_rows, dataset)
    elif dataset.format == DatasetFormats.ANN_DATA:
        content_rows = add_ann_data_content_rows(content_rows, dataset)
    elif dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT:
        content_rows = add_single_cell_experiment_content_rows(content_rows, dataset)

    # SPATIAL get their own row
    if dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT:
        for project in dataset.spatial_projects:
            content_rows.add(
                ContentRow(project, Modalities.SPATIAL, dataset.format, "SPATIAL_LINK")
            )

    # BULK get their own row when data is present
    if dataset.format != DatasetFormats.METADATA:
        for project in dataset.bulk_single_cell_projects:
            content_rows.add(
                ContentRow(project, Modalities.BULK_RNA_SEQ, "BULK_FORMAT", "BULK_LINK")
            )

    return sorted(
        content_rows,
        key=lambda content_row: (content_row.project.scpca_id, content_row.modality),
    )


def get_file_contents_dataset(dataset) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""

    # data that is passed into templates
    context = {
        "context": {
            "date": utils.helpers.get_today_string(),
            "dataset": dataset,
            "content_rows": get_dataset_contents_section(dataset),
        }
    }

    return merge_partials(
        [
            render_to_string(README_ROOT / "1_header.md", **context),
            render_to_string(README_ROOT / "2_contents.md", **context),
            render_to_string(README_ROOT / "3_usage.md", **context),
            render_to_string(README_ROOT / "4_changelog.md", **context),
            render_to_string(README_ROOT / "5_contact.md", **context),
            render_to_string(README_ROOT / "6_citation.md", **context),
            render_to_string(README_ROOT / "7_terms_of_use.md", **context),
        ]
    )


def merge_partials(partials: list[str]):
    """
    Takes a list of rendered templates, strips, removes empty and combines with new line.
    """
    readme_partials = list(filter(None, [p.strip() for p in partials]))

    return "\n\n".join(readme_partials)


def get_file_contents(download_config: Dict, projects: Iterable) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    readme_template_key_parts = [download_config["modality"], download_config["format"]]

    if download_config is common.PORTAL_METADATA_DOWNLOAD_CONFIG:
        readme_template_key_parts = ["METADATA_ONLY"]
    if download_config in common.PROJECT_DOWNLOAD_CONFIGS.values():
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
            "projects": projects,
        },
    ).strip()
