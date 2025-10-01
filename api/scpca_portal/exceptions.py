from typing import Iterable

from scpca_portal.enums import Modalities


class DatasetDataValidationError(ValueError):
    def __init__(self, message: str | None = None):
        default_message = "A validation error occurred with the dataset data attribute."

        message = message or default_message
        super().__init__(message)


class DatasetDataInvalidSampleIDLocationError(DatasetDataValidationError):
    def __init__(self):
        message = "Sample IDs must be inside an Array."
        super().__init__(message)


class DatasetDataInvalidModalityStringError(DatasetDataValidationError):
    def __init__(self, invalid_value: str):
        message = (
            f"Invalid string value for 'single-cell' modality: {invalid_value}. "
            "Allowed string values: 'MERGED'."
        )
        super().__init__(message)


class DatasetDataInvalidSampleIDError(DatasetDataValidationError):
    def __init__(self, sample_id_str: str):
        message = f"Invalid sample ID format: {sample_id_str}."
        super().__init__(message)


class DatasetDataInvalidProjectIDError(DatasetDataValidationError):
    def __init__(self, project_id_str: str):
        message = f"Invalid project ID format: {project_id_str}."
        super().__init__(message)


class DatasetDataInvalidAnndataSpatialCombinationError(DatasetDataValidationError):
    def __init__(self, invalid_project_ids: Iterable[str]):
        message = (
            "Datasets with format ANN_DATA "
            "do not support projects with SPATIAL samples. "
            f"Invalid projects: {', '.join(sorted(invalid_project_ids))}"
        )
        super().__init__(message)


class DatasetDataProjectsDontExistError(DatasetDataValidationError):
    def __init__(self, invalid_project_ids: Iterable[str]):
        message = f"The following projects do not exist: {', '.join(sorted(invalid_project_ids))}"
        super().__init__(message)


class DatasetDataProjectsNoMergedFilesError(DatasetDataValidationError):
    def __init__(self, invalid_project_ids: Iterable[str]):
        message = (
            "The following projects do not have merged files: "
            f"{', '.join(sorted(invalid_project_ids))}"
        )
        super().__init__(message)


class DatasetDataProjectsNoBulkDataError(DatasetDataValidationError):
    def __init__(self, invalid_project_ids: Iterable[str]):
        message = (
            "The following projects do not have bulk data: "
            f"{', '.join(sorted(invalid_project_ids))}"
        )
        super().__init__(message)


class DatasetDataSamplesDontExistError(DatasetDataValidationError):
    def __init__(self, invalid_sample_ids: Iterable[str]):
        message = f"The following samples do not exist: {', '.join(sorted(invalid_sample_ids))}"
        super().__init__(message)


class DatasetDataSampleAssociationsError(DatasetDataValidationError):
    def __init__(self, project_id: str, modality: Modalities, invalid_sample_ids: Iterable[str]):
        message = (
            "The following samples are not associated "
            f"with {project_id} and {modality}: "
            f"{', '.join(sorted(invalid_sample_ids))}"
        )
        super().__init__(message)
