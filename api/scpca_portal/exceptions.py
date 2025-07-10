class DatasetError(Exception):
    def __init__(self, message=None):
        default_message = "A dataset error occurred."
        super().__init__(message or default_message)


class DatasetLockedProjectError(DatasetError):
    def __init__(self):
        message = "Dataset has a locked project."
        super().__init__(message)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self):
        message = "Unable to find libraries for Dataset."
        super().__init__(message)


class JobError(Exception):
    def __init__(self, message=None):
        default_message = "A job error occurred."
        super().__init__(message or default_message)


class JobSubmitNotPendingError(JobError):
    def __init__(self):
        message = "Job is not in a pending state."
        super().__init__(message)


class JobSubmissionFailedError(JobError):
    def __init__(self):
        message = "Error submitting job to Batch."
        super().__init__(message)


class JobInvalidRetryStateError(JobError):
    def __init__(self):
        message = "Jobs in final states cannot be retried."
        super().__init__(message)
