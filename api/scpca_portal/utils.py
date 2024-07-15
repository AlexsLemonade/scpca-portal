"""Misc utils."""
import subprocess
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)


def boolean_from_string(value: str) -> bool:
    """
    Returns True if string value represents truthy value. Otherwise returns False.
    Raises ValueError if value cannot be casted to boolean.
    """

    value_type = type(value)

    if value_type is bool:
        return value

    if value_type is not str:
        raise ValueError(f"Invalid value: expected str got {value_type}.")

    return value.lower() in ("t", "true")


def join_workflow_versions(workflow_versions: Set) -> str:
    """Returns list of sorted unique workflow versions."""

    return ", ".join(sorted(set(workflow_versions)))


def get_today_string(format: str = "%Y-%m-%d") -> str:
    """Returns today's date formatted. Defaults to ISO 8601."""
    return datetime.today().strftime(format)


def filter_dict_list_by_keys(
    list_of_dicts: List[Dict], included_keys: Set, *, ignore_value_error: bool = True
) -> List[Dict]:
    """
    Returns a list of dictionaries with keys filtered according to provided include_keys.
    If included-keys are not a subset of dictionary keys, returns a ValueError.
    Throwing of ValueError can be disabled.
    """
    # Make sure included_keys is subset of each dictionaries' set of keys
    if not ignore_value_error:
        if any(not set(included_keys).issubset(dictionary) for dictionary in list_of_dicts):
            raise ValueError("Included keys must be a subset of each dictionary's key set")

    new_list_of_dicts = []
    for dictionary in list_of_dicts:
        dictionary_copy = dictionary.copy()
        for key in dictionary.keys():
            if key not in included_keys:
                dictionary_copy.pop(key)
        new_list_of_dicts.append(dictionary_copy)

    return new_list_of_dicts


def get_keys_from_dicts(dicts: List[Dict]) -> Set:
    """Takes a list of dictionaries and returns a set equal to the union of their keys."""
    return set(k for d in dicts for k in d.keys())


def get_sorted_field_names(fieldnames: List | Set) -> List:
    """
    Returns a list of field names based on the METADATA_COLUMN_SORT_ORDER list, and append names
    that are not in the list to the end.
    """
    return sorted(
        sorted(fieldnames, key=str.lower),  # Sort fieldnames first
        key=lambda k: (
            common.METADATA_COLUMN_SORT_ORDER.index(k)
            if k in common.METADATA_COLUMN_SORT_ORDER
            else common.METADATA_COLUMN_SORT_ORDER.index("*")  # Insert additional metadata
        ),
    )


def get_csv_zipped_values(
    data: Dict,
    *args: List[str],
    delimiter: str = common.CSV_MULTI_VALUE_DELIMITER,
) -> List:
    """
    Splits a collection of concatenated strings into new iterables,
    zips together the values within the new iterables which share the same index,
    and returns the zipped values as a list.
    """
    return list(zip(*(data.get(key).split(delimiter) for key in args), strict=True))


"""
The `aws s3 ls <bucket>` command called in `list_s3_paths()` returns a list of two types of entries:
- Bucket Object Entries
- Bucket Prefix Entries
In order to create a standard API, where `entry.file_path` could be accessed
irrespective of the entry type, we've created two named tuples which follow the return format
of each of the bucket entry types.
"""
BucketObjectEntry = namedtuple("BucketObjectEntry", ["date", "time", "size_in_bytes", "file_path"])
BucketPrefixEntry = namedtuple("BucketPrefixEntry", ["prefix_designation", "file_path"])


def list_s3_paths(
    relative_path: Path = Path(),
    *,
    bucket_path: Path = Path(common.INPUT_BUCKET_NAME),
    recursive: bool = True,
):
    """
    Queries a path on an inputted s3 bucket
    and returns bucket's existing content as a list of Path objects.

    The `aws s3 ls <bucket>` command returns a list of two types of entries:
    - Bucket Object Entries
    - Bucket Prefix Entries
    In order to create a standard API, where `entry.file_path` could be accessed
    irrespective of the entry type, we've created two named tuples which follow the return format
    of each of the bucket entry types.
    """
    root_path = Path().joinpath(*bucket_path.parts, *relative_path.parts)
    command_inputs = ["aws", "s3", "ls", f"s3://{root_path}"]

    if recursive:
        command_inputs.append("--recursive")

    if "public" in str(bucket_path):
        command_inputs.append("--no-sign-request")

    try:
        result = subprocess.run(command_inputs, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as error:
        logger.error(
            """
            `{}`: Cause of error not returned, note: folder must exist and be non-empty
            """.format(
                error
            )
        )
        return []

    bucket_entries = []
    for line in output.splitlines():
        if line.strip().startswith("PRE"):
            bucket_entries.append(BucketPrefixEntry._make(line.split()))
        else:
            bucket_entries.append(BucketObjectEntry._make(line.split()))

    # bucket_path may contain nested keys, we want to omit these in returned paths
    bucket_keys = Path().joinpath(*bucket_path.parts[1:])
    # recursive returns an absolute path, so we need to remove the bucket prefix before returning
    if recursive:
        return [Path(entry.file_path).relative_to(bucket_keys) for entry in bucket_entries]
    # non recursive already returns a relative path
    else:
        return [Path(entry.file_path) for entry in bucket_entries]
