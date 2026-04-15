from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scpca_portal.models import DatasetABC


class DatasetError(Exception):
    def __init__(self, message: str | None = None, dataset: "DatasetABC" = None) -> None:
        default_message = "A dataset error occurred."

        message = message or default_message
        if dataset:
            message = f"Dataset {dataset.id}: {message}"
        super().__init__(message)


class DatasetLockedProjectError(DatasetError):
    def __init__(self, dataset: "DatasetABC" = None) -> None:
        message = "Dataset has a locked project."
        super().__init__(message, dataset)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self, dataset: "DatasetABC" = None) -> None:
        message = "Unable to find libraries for Dataset."
        super().__init__(message, dataset)
