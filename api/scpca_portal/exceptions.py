from typing import Iterable

from django.template.defaultfilters import pluralize

from scpca_portal.enums import Modalities


# scpca_portal.batch
class BatchError(Exception):
    def __init__(self, message: str | None = None, job=None, job_ids=None):
        default_message = "An error occurred while communicating with AWS Batch API."
        message = message or default_message
        super().__init__(message)
        # For logging
        self.job = job
        self.job_ids = job_ids


class BatchGetJobsFailedError(BatchError):
    def __init__(self, job_ids=None):
        job_ids = job_ids or []
        if job_ids:
            message = (
                f"Failed to fetch AWS Batch job{pluralize(len(job_ids))} "
                f"for job ID{pluralize(len(job_ids))}: {', '.join(job_ids)}"
            )
        else:
            message = "Failed to fetch AWS Batch jobs: no job IDs."
        super().__init__(message, job_ids=job_ids)


class DatasetError(Exception):
    def __init__(self, message: str | None = None, dataset=None):
        default_message = "A dataset error occurred."

        message = message or default_message
        if dataset:
            message = f"Dataset {dataset.id}: {message}"
        super().__init__(message)


class DatasetLockedProjectError(DatasetError):
    def __init__(self, dataset=None):
        message = "Dataset has a locked project."
        super().__init__(message, dataset)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self, dataset=None):
        message = "Unable to find libraries for Dataset."
        super().__init__(message, dataset)


class JobError(Exception):
    def __init__(self, message: str | None = None, job=None):
        default_message = "A job error occurred."

        message = message or default_message
        if job:
            message = f"Job {job.id}: {message}"
        super().__init__(message)


class JobSubmitNotPendingError(JobError):
    def __init__(self, job=None):
        message = "Job is not in a pending state."
        super().__init__(message, job)


class JobSyncNotProcessingError(JobError):
    def __init__(self, job=None):
        message = "Job is not in a processing state."
        super().__init__(message, job)


class JobSubmissionFailedError(JobError):
    def __init__(self, job=None):
        message = "Error submitting job to Batch."
        super().__init__(message, job)


class JobInvalidRetryStateError(JobError):
    def __init__(self, job=None):
        message = "Jobs in final states cannot be retried."
        super().__init__(message, job)


class JobInvalidTerminateStateError(JobError):
    def __init__(self, job=None):
        message = "Jobs in final states cannot be terminated."
        super().__init__(message, job)


class JobSyncStateFailedError(JobError):
    def __init__(self, job=None):
        message = "Error syncing job state with Batch."
        super().__init__(message, job)


class JobTerminationFailedError(JobError):
    def __init__(self, job=None):
        message = "Error terminating job in Batch."
        super().__init__(message, job)


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
