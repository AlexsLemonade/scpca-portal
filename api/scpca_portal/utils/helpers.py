"""Misc utils."""

import hashlib
import inspect
import math
import shutil
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Set, Tuple

from django.conf import settings

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)


def remove_data_dirs(
    wipe_input_dir: bool = True,
    wipe_output_dir: bool = True,
    input_dir: Path = settings.INPUT_DATA_PATH,
    output_dir: Path = settings.OUTPUT_DATA_PATH,
) -> None:
    """
    Removes the input and/or output data directories based on the given wipe flags.
    Validates input_dir/output_dir to ensure they are within the data directories before removal.
    Raises an exception if not.
    """
    # Ensure input_dir/output_dir are within the data directories
    base_input_dir = settings.INPUT_DATA_PATH
    base_output_dir = settings.OUTPUT_DATA_PATH

    if wipe_input_dir:
        if not input_dir.is_relative_to(base_input_dir):
            raise Exception(f"{input_dir} must be within the {base_input_dir} directory.")
        shutil.rmtree(input_dir, ignore_errors=True)
    if wipe_output_dir:
        if not output_dir.is_relative_to(base_output_dir):
            raise Exception(f"{output_dir} must be within the {base_output_dir} directory.")
        shutil.rmtree(output_dir, ignore_errors=True)


def create_data_dirs(
    wipe_input_dir: bool = False,
    wipe_output_dir: bool = True,
    input_dir: Path = settings.INPUT_DATA_PATH,
    output_dir: Path = settings.OUTPUT_DATA_PATH,
) -> None:
    """
    Creates the input and/or output data directories.
    Directories are wiped first based on the given wipe flags:
     - wipe_input_dir defaults to False. Input files are typically preserved between
        testing rounds to speed up our tests.
      - wipe_output_dir defaults to True. Computed files are typically removed after execution.
    Callers can adjust the dafault behavior as necessary.

    NOTE: Passing a directory outside the data directories is not allowed.
    """
    remove_data_dirs(
        wipe_input_dir=wipe_input_dir,
        wipe_output_dir=wipe_output_dir,
        input_dir=input_dir,
        output_dir=output_dir,
    )
    input_dir.mkdir(exist_ok=True, parents=True)
    output_dir.mkdir(exist_ok=True, parents=True)


def remove_nested_data_dirs(
    data_dir: str, wipe_input_dir: bool = True, wipe_output_dir: bool = False
) -> None:
    """
    Removes the given nested folder within the input and/or output data directories.
    By default, only wipes the nested folder in the input directory.
    """
    remove_data_dirs(
        wipe_input_dir,
        wipe_output_dir,
        input_dir=settings.INPUT_DATA_PATH / data_dir,
        output_dir=settings.OUTPUT_DATA_PATH / data_dir,
    )


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


def string_from_list(value: Any, delimiter=";") -> Any:
    """
    Returns a delimited string converted from a list. Otherwise returns value.
    """
    return delimiter.join(value) if isinstance(value, list) else value


def join_workflow_versions(workflow_versions: Iterable) -> str:
    """Returns list of sorted unique workflow versions."""

    return ", ".join(sorted(set(workflow_versions)))


def get_chunk_list(list: List[Any], size: int) -> Generator[List[Any], None, None]:
    """
    Yields chunks of the given list with the specified size.
    """
    for i in range(0, len(list), size):
        yield list[i : i + size]


def get_docs_url(path: str) -> str:
    """
    Returns the full ScPCA docs URL for the given path.
    """
    DOCS_BASE = "https://scpca.readthedocs.io/en"
    DOCS_VERSION = "stable"

    if settings.ENABLE_FEATURE_PREVIEW:
        DOCS_VERSION = "development"

    return f"{DOCS_BASE}/{DOCS_VERSION}/{path}"


def get_today_string(format: str = "%Y-%m-%d") -> str:
    """Returns today's date formatted. Defaults to ISO 8601."""
    return datetime.today().strftime(format)


def filter_dict_by_keys(dictionary: Dict[str, Any], included_keys: Set[str]) -> Dict[str, Any]:
    """Returns a filtered version of the input dict according to set of included keys."""
    return {k: v for k, v in dictionary.items() if k in included_keys}


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

    return [filter_dict_by_keys(dictionary, included_keys) for dictionary in list_of_dicts]


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


def get_sorted_modalities(modalities: List | Set) -> List:
    """
    Returns a list of sorted modality values.
    By default, SINGLE_CELL always comes first.
    """
    return sorted(
        sorted(modalities),  # Sort modalities first
        key=lambda m: (common.MODALITIES_DEFAULT_SORT_ORDER.index(m)),
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
    # Fallback to an empty string for missing keys
    return list(zip(*(data.get(key, "").split(delimiter) for key in args), strict=True))


KeyTransform = namedtuple("KeyTransform", ["old_key", "new_key", "default_value"])


def transform_keys(data_dict: Dict, key_transforms: List[Tuple]):
    """
    Transforms keys in inputted data dict according to inputted key transforms tuple list.
    """
    for element in [KeyTransform._make(element) for element in key_transforms]:
        if element.old_key in data_dict:
            data_dict[element.new_key] = data_dict.pop(element.old_key, element.default_value)

    return data_dict


def transform_values(data_dict: Dict, value_transforms: Dict[str, Callable], *args):
    """
    Transform values in data dict according to transformation functions in value transform dict.
    Functions with variable numbers of params are supported,
    where passed params are trimmed dynamically to the param length of each function.
    """
    for key, func in value_transforms.items():
        func_params = inspect.signature(func).parameters
        # trim additional args based on number of func params
        adtl_args = args[: (len(func_params) - 1)]

        data_dict[key] = func(data_dict[key], *adtl_args)

    return data_dict


def find_first_contained(value: Any, containers: Iterable[Iterable[Any]]) -> Iterable[Any] | None:
    """
    Return first occurrence of container which contains the passed value.
    """
    return next((container for container in containers if value in container), None)


def path_replace(path: Path, old_value: str, new_value: str) -> Path:
    """Return path with all occurrences of old_value replaced with new_value."""
    return Path(str(path).replace(old_value, new_value))


def format_bytes(size_in_bytes: int) -> str:
    """
    Return a formatted string of the passed value converted from bytes to a more appropriate size.
    """
    # This function was inspired by https://stackoverflow.com/a/18650828/763705.

    if size_in_bytes < 0:
        raise ValueError("size in bytes must be a positive number.")

    k = 1024
    if size_in_bytes < k:
        return f"{size_in_bytes} Bytes"

    sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = math.floor(math.log(size_in_bytes) / math.log(k))
    return f"{size_in_bytes / k**i:.2f} {sizes[i]}"


def hash_values(values: List[str]) -> str:
    """
    Return the hash value of a passed list of strings.
    """
    md5_hasher = hashlib.md5()

    for value in sorted(values):
        md5_hasher.update(value.encode("utf-8"))

    return md5_hasher.hexdigest()
