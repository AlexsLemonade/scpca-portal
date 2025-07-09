class JobErrorMessages:
    NOT_PENDING = "Job is not in a pending state."
    MAX_ATTEMPTS_EXCEEDED = "Maximum job retry attempts exceeded."
    SUBMISSION_FAILED = "Error submitting job to Batch."
    INVALID_RETRY_STATE = "Jobs in final states cannot be retried."


class DatasetErrorMessages:
    HAS_LOCKED_PROJECTS = "Dataset has a locked project."
    NO_LIBRARIES = "Unable to find libraries for Dataset."
