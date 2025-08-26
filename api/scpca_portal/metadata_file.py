import csv
import io
from typing import Dict, List

from scpca_portal import common, utils


class MetadataFilenames:
    SINGLE_CELL_METADATA_FILE_NAME = "single_cell_metadata.tsv"
    SPATIAL_METADATA_FILE_NAME = "spatial_metadata.tsv"
    METADATA_ONLY_FILE_NAME = "metadata.tsv"


def get_file_name(download_config: Dict) -> str:
    """Return metadata file name according to passed download_config."""
    if download_config.get("metadata_only", False):
        return MetadataFilenames.METADATA_ONLY_FILE_NAME

    return getattr(MetadataFilenames, f'{download_config["modality"]}_METADATA_FILE_NAME')


def get_file_contents(libraries_metadata: List[Dict], **kwargs) -> str:
    """Return newly genereated metadata file as a string for immediate writing to a zip archive."""
    formatted_libraries_metadata = [format_metadata_dict(lib_md) for lib_md in libraries_metadata]
    sorted_libraries_metadata = sorted(
        formatted_libraries_metadata,
        key=lambda k: (k[common.PROJECT_ID_KEY], k[common.SAMPLE_ID_KEY], k[common.LIBRARY_ID_KEY]),
    )

    kwargs["fieldnames"] = kwargs.get(
        "fieldnames",
        utils.get_sorted_field_names(utils.get_keys_from_dicts(sorted_libraries_metadata)),
    )
    kwargs["delimiter"] = kwargs.get("delimiter", common.TAB)
    # By default fill dicts with missing fieldnames with "NA" values
    kwargs["restval"] = kwargs.get("restval", common.NA)

    with io.StringIO() as metadata_buffer:
        # Write libraries metadata to buffer
        csv_writer = csv.DictWriter(metadata_buffer, **kwargs)
        csv_writer.writeheader()
        csv_writer.writerows(sorted_libraries_metadata)

        return metadata_buffer.getvalue()


def format_metadata_dict(metadata_dict: Dict) -> Dict:
    """
    Returns a copy of metadata dict that is formatted and ready to be written to file.
    """
    return {k: utils.string_from_list(v) for k, v in metadata_dict.items()}
