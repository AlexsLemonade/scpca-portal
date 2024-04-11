"""Misc utils."""
from datetime import datetime
from typing import Any, Dict, List


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


def sum_key(key: str, listOfDicts: List[Dict]) -> int:
    """Returns the sum of values referenced by the same key within multiple dictionaries."""
    return sum([dictionary.get(key, 0) for dictionary in listOfDicts])


def filter_key(key: str, listOfDicts: List[Dict]) -> str:
    """Iterates over a list of dictionaries, filters out the value of a chosen key,
    and returns a list of all values."""
    return [dictionary.get(key).strip() for dictionary in listOfDicts if key in dictionary]


def key_value_exists(key: str, value: Any, listOfDicts: List[Dict]) -> bool:
    """Returns True if provided key exists with provided value in list of dictionaries,
    else returns False."""
    return bool([dictionary.get(key) for dictionary in listOfDicts if dictionary.get(key) == value])
