"""Misc utils."""


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
    """Returns list of sorted workflow versions."""

    return ", ".join(sorted(workflow_versions))
