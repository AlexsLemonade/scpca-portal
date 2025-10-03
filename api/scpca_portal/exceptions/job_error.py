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
