from collections import defaultdict
from typing import Dict, Iterable

from django.conf import settings
from django.template.loader import render_to_string

from scpca_portal import common, utils  # ccdl_datasets,
from scpca_portal.enums import DatasetFormats, Modalities

# from scpca_portal.enums import CCDLDatasetNames

OUTPUT_NAME = "README.md"

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "readme"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "readme.md"

# Dataset Readme Templates
README_ROOT = settings.TEMPLATE_PATH / "dataset_readme"
HEADER_TEMPLATE = README_ROOT / "header/index.md"
USAGE_TEMPLATE = README_ROOT / "usage/index.md"
CHANGELOG_TEMPLATE = README_ROOT / "changelog/index.md"
CONTACT_TEMPLATE = README_ROOT / "contact/index.md"
CITATION_TEMPLATE = README_ROOT / "citation/index.md"
TERMS_TEMPLATE = README_ROOT / "terms_of_use/index.md"


# Contents
DATASET_CONTENTS_ROOT = README_ROOT / "contents"


def merge_partials(partials: list[str]):
    """
    Takes a list of rendered templates, strips, removes empty and combines with new line.
    """
    # For the conte
    readme_partials: list[str] = list(filter(None, [p.strip() for p in partials]))

    return "\n".join(readme_partials)


def get_contents_dict(dataset) -> dict:
    """Takes dataset and returns dictionary that relates the content template to the projects that it applies to."""

    # body is a dict where the key is the relative template path
    # and the value is a list of project ids that apply to that content section
    # ex: {
    #    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT.md": ["SCPCP0000000"],
    #    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.md": ["SCPCP999999"]
    # }

    body = defaultdict(set)

    # metadata can't be combined
    if dataset.format == DatasetFormats.METADATA:
        body["METADATA.md"] = dataset.data.keys()
        return body

    # project data types
    for project, project_options in dataset.data.items():
        if single_cell_samples := dataset.single_cell_samples.filter(
            project__scpca_id=project
        ):
            # template are named "<DatasetFormats>_<Modalities>_<MERGED|MULTIPLEXED?>.md"
            template_name_parts = [dataset.format, Modalities.SINGLE_CELL]

            # multiplexed and merged are mutually exclusive
            if project_options.get("merge_single_cell", False):
                template_name_parts.append("MERGED")
            elif (
                dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT
                and single_cell_samples.filter(has_multiplexed_data=True).exists()
            ):
                template_name_parts.append("MULTIPLEXED")

            body[f"{'_'.join(template_name_parts)}.md"].add(project)

        if (
            dataset.format == DatasetFormats.SINGLE_CELL_EXPERIMENT
            and dataset.spatial_samples.filter(project__scpca_id=project).exists()
        ):
            body[f"{dataset.format}_{Modalities.SPATIAL}.md"].add(project)

    return body


def get_file_contents_dataset(dataset) -> str:
    """Return newly generated readme file as a string for immediate writing to a zip archive."""

    # data that is passed into templates
    context = {
        "context": {
            "date": utils.helpers.get_today_string(),
            "dataset": dataset,
        }
    }

    # render the contents section before combining the entire readme
    contents_section = merge_partials(
        [
            render_to_string(
                DATASET_CONTENTS_ROOT / template,
                context={
                    "dataset": dataset,
                    "projects": dataset.projects.filter(scpca_id__in=project_ids),
                },
            )
            for template, project_ids in get_contents_dict(dataset).items()
        ]
    )

    # For the conte
    return merge_partials(
        [
            render_to_string(HEADER_TEMPLATE, **context),
            contents_section,
            render_to_string(USAGE_TEMPLATE, **context),
            render_to_string(CHANGELOG_TEMPLATE, **context),
            render_to_string(CONTACT_TEMPLATE, **context),
            render_to_string(CITATION_TEMPLATE, **context),
            render_to_string(TERMS_TEMPLATE, **context),
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
    contents_template = (
        f"{TEMPLATE_ROOT}/contents/{'_'.join(readme_template_key_parts)}.md"
    )

    return render_to_string(
        TEMPLATE_FILE_PATH,
        context={
            "date": utils.get_today_string(),
            "download_config": download_config,
            "contents_template": contents_template,
            "projects": projects,
        },
    ).strip()
