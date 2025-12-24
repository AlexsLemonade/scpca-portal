import re
from collections import namedtuple
from typing import Dict, Iterable

from django.conf import settings
from django.template.loader import render_to_string

from scpca_portal import common, utils  # ccdl_datasets,
from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, FileFormats, Modalities

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"

# Dataset Readme Templates
README_ROOT = settings.TEMPLATE_PATH / "dataset_readme"


METADATA_LINK = utils.get_docs_url("download_files.html#metadata")
ANN_DATA_LINK = utils.get_docs_url("sce_file_contents.html#components-of-an-anndata-object")
ANN_DATA_WITH_CITE_SEQ_LINK = utils.get_docs_url(
    "sce_file_contents.htm#additional-anndata-components-for-cite-seq-libraries-with-adt-tags"
)
ANN_DATA_MERGED_LINK = utils.get_docs_url(
    "merged_objects.html#components-of-an-anndata-merged-object"
)
ANN_DATA_MERGED_WITH_CITE_SEQ_LINK = utils.get_docs_url(
    "merged_objects.html#additional-anndata-components-for-cite-seq-libraries-with-adt-tags"
)
SINGLE_CELL_EXPERIMENT_LINK = utils.get_docs_url(
    "sce_file_contents.html#components-of-a-singlecellexperiment-object"
)
SINGLE_CELL_EXPERIMENT_MERGED_LINK = utils.get_docs_url(
    "merged_objects.html#components-of-a-singlecellexperiment-merged-object"
)
SINGLE_CELL_EXPERIMENT_MULTIPLEXED_LINK = utils.get_docs_url(
    "sce_file_contents.html#additional-singlecellexperiment-components-for-multiplexed-libraries"
)
SPATIAL_SPATIAL_SPACERANGER_LINK = utils.get_docs_url(
    "processing_information.html#spatial-transcriptomics"
)
BULK_LINK = utils.get_docs_url("processing_information.html#bulk-rna-samples")

PORTAL_CCDL_DATASET_LINKS = {
    CCDLDatasetNames.ALL_METADATA: utils.get_docs_url("download_files.html#portal-wide-downloads"),
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT: utils.get_docs_url(
        "download_files.html#singlecellexperiment-portal-wide-download-structure"
    ),
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: utils.get_docs_url(
        "download_files.html"
        "#portal-wide-download-structure-for-merged-singlecellexperiment-objects"
    ),
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA: utils.get_docs_url(
        "download_files.html#anndata-portal-wide-download-structure"
    ),
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED: utils.get_docs_url(
        "download_files.html#portal-wide-download-structure-for-merged-anndata-objects"
    ),
    CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER: utils.get_docs_url(
        "download_files.html#spatial-portal-wide-download-structure"
    ),
}

# used in get_content_table_rows and in 2_contents.md
ContentRow = namedtuple("ContentRow", ["project", "modality", "format", "docs"])

# used to map the human-readable values to the corresponding format and modality tokens
FORMAT_STRING = {
    "SINGLE_CELL_EXPERIMENT": FileFormats.SINGLE_CELL_EXPERIMENT.label,
    "ANN_DATA": FileFormats.ANN_DATA.label,
    "BULK_FORMAT": "Bulk Format",
    "SPATIAL_SPACERANGER": FileFormats.SPATIAL_SPACERANGER.label,
}
MODALITY_STRING = {
    Modalities.BULK_RNA_SEQ: Modalities.BULK_RNA_SEQ.label,
    Modalities.SINGLE_CELL: Modalities.SINGLE_CELL.label,
    Modalities.SPATIAL: Modalities.SPATIAL.label,
}


def add_ann_data_content_rows(content_rows: set, dataset) -> set:
    """
    Takes a dataset and returns the set of ContentRows
    for the content section table for ANN_DATA.
    """
    # SINGLE_CELL
    for project in dataset.single_cell_projects:
        # ANN_DATA
        docs_link = ANN_DATA_LINK

        # HAS CITE-SEQ
        if project.has_cite_seq_data:
            docs_link = ANN_DATA_WITH_CITE_SEQ_LINK

        # ANN_DATA_MERGED
        if dataset.get_is_merged_project(project.scpca_id):
            docs_link = ANN_DATA_MERGED_LINK
            # ANN_DATA_MERGED_WITH_CITE
            if project.has_cite_seq_data:
                docs_link = ANN_DATA_MERGED_WITH_CITE_SEQ_LINK

        content_rows.add(
            ContentRow(
                project,
                MODALITY_STRING[Modalities.SINGLE_CELL],
                FORMAT_STRING[dataset.format],
                docs_link,
            )
        )

    return content_rows


def add_single_cell_experiment_content_rows(content_rows: set, dataset) -> set:
    """
    Takes a dataset and returns the set of ContentRows
    for the content section table for SINGLE_CELL_EXPERIMENT.
    """
    # SINGLE_CELL
    for project in dataset.single_cell_projects:
        # SINGLE_CELL_EXPERIMENT
        docs_link = SINGLE_CELL_EXPERIMENT_LINK

        # SINGLE_CELL_EXPERIMENT_MERGED
        if dataset.get_is_merged_project(project.scpca_id):
            docs_link = SINGLE_CELL_EXPERIMENT_MERGED_LINK
        # SINGLE_CELL_EXPERIMENT_MULTIPLEXED
        elif (
            dataset.get_project_modality_samples(project.scpca_id, Modalities.SINGLE_CELL)
            .filter(has_multiplexed_data=True)
            .exists()
        ):
            docs_link = SINGLE_CELL_EXPERIMENT_MULTIPLEXED_LINK

        content_rows.add(
            ContentRow(
                project,
                MODALITY_STRING[Modalities.SINGLE_CELL],
                FORMAT_STRING[dataset.format],
                docs_link,
            )
        )

    return content_rows


def get_content_table_rows(dataset) -> list[ContentRow]:
    """
    Returns a list of ContentRows for non-metadata downloads.
    """
    # No table for metadata downloads
    if dataset.format == DatasetFormats.METADATA:
        return []

    # Metadata
    content_rows: set[ContentRow] = set()

    # These rows depend on the format
    if dataset.format == DatasetFormats.ANN_DATA:
        content_rows = add_ann_data_content_rows(content_rows, dataset)
    elif dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT:
        content_rows = add_single_cell_experiment_content_rows(content_rows, dataset)

    # SPATIAL get their own row
    for project in dataset.spatial_projects:
        content_rows.add(
            ContentRow(
                project,
                MODALITY_STRING[Modalities.SPATIAL],
                FORMAT_STRING[FileFormats.SPATIAL_SPACERANGER],
                SPATIAL_SPATIAL_SPACERANGER_LINK,
            )
        )

    # BULK get their own row when data is present
    if dataset.format != DatasetFormats.METADATA:
        for project in dataset.bulk_single_cell_projects:
            content_rows.add(
                ContentRow(
                    project,
                    MODALITY_STRING[Modalities.BULK_RNA_SEQ],
                    FORMAT_STRING["BULK_FORMAT"],
                    BULK_LINK,
                )
            )

    return sorted(
        content_rows,
        key=lambda content_row: (content_row.project.scpca_id, content_row.modality),
    )


def get_content_portal_wide_link(dataset):
    """
    Returns the link to the documentation if dataset is a ccdl portal wide download
    """
    if dataset.is_ccdl and not dataset.ccdl_project_id:
        return PORTAL_CCDL_DATASET_LINKS.get(dataset.ccdl_name)
    return None


def get_content_metadata_link(dataset):
    """
    Returns the link to the documentation if dataset is for metadata.
    Portal wide metadata is handled by `content_portal_wide_link`.
    """
    if dataset.format == DatasetFormats.METADATA and dataset.ccdl_project_id:
        return METADATA_LINK
    return None


def get_file_contents_dataset(dataset) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""

    # data that is passed into templates
    context = {
        "context": {
            "date": utils.helpers.get_today_string(),
            "dataset": dataset,
            "content_portal_wide_link": get_content_portal_wide_link(dataset),
            "content_metadata_link": get_content_metadata_link(dataset),
            "content_table_rows": get_content_table_rows(dataset),
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
    Also replaces anything greater than 2 new lines with 2 newlines.
    """
    readme_partials = list(filter(None, [re.sub(r"\n\n+", "\n\n", p.strip()) for p in partials]))

    return "\n\n".join(readme_partials)


def get_file_contents(download_config: Dict, projects: Iterable) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""
    # TODO: when computed file is removed update template name to match ccdl dataset name
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
