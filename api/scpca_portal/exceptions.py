from scpca_portal.enums import ErrorMessages


class JobError(Exception):
    """Base exception for job-related errors."""

    def __init__(self, message=None):
        super().__init__(message or ErrorMessages.JOB_GENERIC)


class DatasetError(Exception):
    """Base exception for dataset-related errors."""

    def __init__(self, message=None):
        super().__init__(message or ErrorMessages.DATASET_GENERIC)
