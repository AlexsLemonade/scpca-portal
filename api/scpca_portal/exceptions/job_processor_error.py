class JobProcessorError(NotImplementedError):
    def __init__(self, class_name: str, *missing: str):
        super().__init__(f"{class_name} must implement: {', '.join(missing)}")


class JobProcessorStepNotImplementedError(JobProcessorError):
    pass


class JobProcessorHandlerNotImplementedError(JobProcessorError):
    pass


class JobProcessorHandlerStepNotImplementedError(JobProcessorError):
    pass
