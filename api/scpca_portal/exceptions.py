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


class JobTerminationFailedError(JobError):
    def __init__(self, job=None):
        message = "Error terminating job in Batch."
        super().__init__(message, job)
