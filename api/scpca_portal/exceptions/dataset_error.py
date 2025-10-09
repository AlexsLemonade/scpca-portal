from rest_framework import status
from rest_framework.exceptions import APIException


class DatasetError(Exception):
    def __init__(self, message: str | None = None, dataset=None):
        default_message = "A dataset error occurred."

        message = message or default_message
        if dataset:
            message = f"Dataset {dataset.id}: {message}"
        super().__init__(message)


class DatasetFormatChangeError(DatasetError):
    def __init__(self):
        message = "Dataset with data cannot change format."
        super().__init__(message)


class DatasetLockedProjectError(DatasetError):
    def __init__(self, dataset=None):
        message = "Dataset has a locked project."
        super().__init__(message, dataset)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self, dataset=None):
        message = "Unable to find libraries for Dataset."
        super().__init__(message, dataset)


class UpdateProcessingDatasetError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Invalid request: Processing datasets cannot be modified."
    default_code = "conflict"
