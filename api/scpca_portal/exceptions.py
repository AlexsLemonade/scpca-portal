from scpca_portal.enums import ErrorMessages


class DatasetError(Exception):
    def __init__(self, message=None):
        super().__init__(message or ErrorMessages.DATASET_GENERIC)


class DatasetLockedProjectError(DatasetError):
    def __init__(self):
        super().__init__(ErrorMessages.DATASET_LOCKED_PROJECT)


class DatasetMissingLibrariesError(DatasetError):
    def __init__(self):
        super().__init__(ErrorMessages.DATASET_NO_LIBRARIES)


class JobError(Exception):
    def __init__(self, message=None):
        super().__init__(message or ErrorMessages.JOB_GENERIC)


class JobNotPendingError(JobError):
    def __init__(self):
        super().__init__(ErrorMessages.JOB_NOT_PENDING)


class JobSubmissionFailedError(JobError):
    def __init__(self):
        super().__init__(ErrorMessages.JOB_SUBMISSION_FAILED)


class JobInvalidRetryStateError(JobError):
    def __init__(self):
        super().__init__(ErrorMessages.JOB_INVALID_RETRY_STATE)
