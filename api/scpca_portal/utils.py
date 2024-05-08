"""Misc utils."""
from datetime import datetime


def boolean_from_string(value):
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


def join_workflow_versions(workflow_versions):
    """Returns list of sorted unique workflow versions."""

    return ", ".join(sorted(set(workflow_versions)))


def get_today_string(format: str = "%Y-%m-%d"):
    """Returns today's date formatted. Defaults to ISO 8601."""
    return datetime.today().strftime(format)


def filter_dict_list_by_keys(list_of_dicts, included_keys, *, ignore_value_error=True):
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
