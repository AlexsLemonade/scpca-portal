from typing import Dict, Iterable
from collections import namedtuple

from django.conf import settings
from django.template.loader import render_to_string

from scpca_portal import common, utils  # ccdl_datasets,

from scpca_portal.enums import DatasetFormats, DatasetDataProjectConfig, Modalities

# from scpca_portal.enums import CCDLDatasetNames

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"

# Dataset Readme Templates
README_ROOT = settings.TEMPLATE_PATH / "dataset_readme"

# used in get_dataset_contents_section and in 2_contents.md
ContentRow = namedtuple("ContentRow", ["project", "modality", "format", "docs"])


def get_dataset_contents_section(dataset):
    # tuple is (project_id, project_url, modality, format, docs_link)

    # Metadata
    if dataset.format == DatasetFormats.METADATA:
        return [
            ContentRow(project, project.modalities, "NA", "METADATA")
            for project in dataset.projects
        ]

    # projects_dict = {project.scpca_id: project for project in dataset.projects}
    rows = set()

    # SINGLE_CELL
    for project in dataset.single_cell_projects:
        content_dict = {
            "project": project,
            "modality": Modalities.SINGLE_CELL,
            "format": dataset.format,
        }

        # MERGED
        if dataset.data[project.scpca_id].get(DatasetDataProjectConfig.MERGE_SINGLE_CELL):
            if dataset.format == DatasetFormats.ANN_DATA:
                content_dict["docs"] = "MERGED_ANN_DATA"
            else:
                content_dict["docs"] = "MERGED_SINGLE_CELL_EXPERIMENT"

            rows.add(ContentRow(**content_dict))
            continue

        # MULTIPLEXED
        if (
            dataset.get_samples(project.scpca_id, Modalities.SINGLE_CELL)
            and dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT
        ):
            content_dict["docs"] = "MULTIPLEXED_SINGLE_CELL"
            rows.add(ContentRow(**content_dict))
            continue

        # SINGLE_CELL
        content_dict["docs"] = "SINGLE_CELL"
        rows.add(ContentRow(**content_dict))

    # SPATIAL
    if dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT:
        for project in dataset.spatial_projects:
            rows.add(ContentRow(project, Modalities.SPATIAL, dataset.format, "SPATIAL_LINK"))

    # ANN_DATA CITE-SEQ
    if dataset.format == DatasetFormats.ANN_DATA:
        for project in dataset.cite_seq_projects:
            rows.add(
                ContentRow(
                    project,
                    Modalities.CITE_SEQ,
                    dataset.format,
                    "ANN_DATA_CITE_SEQ_LINK",
                )
            )

    # BULK
    for project in dataset.bulk_single_cell_projects:
        rows.add(ContentRow(project, Modalities.BULK_RNA_SEQ, "FORMAT?", "BULK_LINK"))

    return list(rows)


def merge_partials(partials: list[str]):
    """
    Takes a list of rendered templates, strips, removes empty and combines with new line.
    """
    readme_partials: list[str] = list(filter(None, [p.strip() for p in partials]))

    return "\n\n".join(readme_partials)


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
