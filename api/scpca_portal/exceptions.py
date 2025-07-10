class DatasetError(Exception):
    def __init__(self, message=None, dataset_id=None):
        default_message = "A dataset error occurred."

        message = message or default_message
        if dataset_id:
            message = f"Dataset {dataset_id}: {message}"
        super().__init__(message)


class DatasetLockedProjectError(DatasetError):
    def __init__(self, dataset_id=None):
        message = "Dataset has a locked project."
        super().__init__(message, dataset_id)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self, dataset_id=None):
        message = "Unable to find libraries for Dataset."
        super().__init__(message, dataset_id)


class JobError(Exception):
    def __init__(self, message=None, job_id=None):
        default_message = "A job error occurred."

        message = message or default_message
        if job_id:
            message = f"Job {job_id}: {message}"
        super().__init__(message)


class JobSubmitNotPendingError(JobError):
    def __init__(self, job_id=None):
        message = "Job is not in a pending state."
        super().__init__(message, job_id)


class JobSubmissionFailedError(JobError):
    def __init__(self, job_id=None):
        message = "Error submitting job to Batch."
        super().__init__(message, job_id)


class JobInvalidRetryStateError(JobError):
    def __init__(self, job_id=None):
        message = "Jobs in final states cannot be retried."
        super().__init__(message, job_id)
