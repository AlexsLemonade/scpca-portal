"""Misc utils."""

from datetime import datetime
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
