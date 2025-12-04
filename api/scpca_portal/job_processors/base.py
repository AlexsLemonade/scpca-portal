from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Tuple

from scpca_portal.enums import JobStates
from scpca_portal.exceptions import (
    JobProcessorHandlerNotImplementedError,
    JobProcessorHandlerStepNotImplementedError,
    JobProcessorStepNotImplementedError,
)
from scpca_portal.models import Job


class JobProcessorABC(ABC):
    """
    Abstract base class that orchestrates the execution of a series of
    processing *steps* for a Job instance.

    Sub‑classes declare the concrete workflow by providing:

    * ``steps`` – an ordered list of method names (as strings) that will be
      called sequentially when `run` is invoked.
    * ``exception_handlers`` – a mapping whose keys are ``(step_name,
      exception_type)`` tuples and whose values are the names of handler
      methods (as strings) that should be executed when the corresponding
      exception is raised in the given step.

    Step functions take no arguements.
    Exception handler functions take the error as an argument.

    The base class handles the plumbing:

    * Validation that every declared step and handler actually exists and is
      callable.
    * Automatic lookup of the appropriate handler when a step raises an
      exception.
    * Update the Job instance state.
      (e.g. ``PROCESSING`` → ``FAILED`` / ``SUCCEEDED``).
    * Hook methods (`on_*`) that subclasses may override to react to lifecycle
      events such as the start/end of the whole run, the start of a step, or an
      uncaught exception.

    Public Methods
    ---------------
    run() -> None
        Executes each step in order, applying the appropriate exception
        handling logic. Updates the job state to ``FAILED`` if any step raises
        an unhandled exception, otherwise marks the job as ``SUCCEEDED``.

    Hook Methods (override as needed)
    ---------------------------------
    on_run() -> None
        Invoked once before any step is executed.

    on_step_start(step: str) -> None
        Invoked right before a particular step begins execution.

    on_step_exception(step: str, e: Exception) -> None
        Invoked when a step raises an exception that *does* have a registered
        handler. The default implementation does nothing; subclasses can log
        or modify behaviour here.

    on_uncaught_exception(step: str, e: Exception) -> None
        Called when a step raises an exception for which no handler is
        defined. The default implementation does nothing; subclasses can log
        or modify behaviour here.

    on_run_done() -> None
        Invoked after all steps have completed successfully.
    """

    @property
    @abstractmethod
    def steps(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def exception_handlers(self) -> Dict[Tuple[str, type], str]:
        pass

    @property
    def job(self) -> Job:
        """Job should be readonly"""
        return self._job

    def on_run(self):
        pass

    def on_step_start(self, step: str):
        pass

    def on_step_exception(self, step: str, e: Exception):
        pass

    def on_uncaught_exception(self, step, e: Exception):
        pass

    def on_run_done(self):
        pass

    def __init__(self, job: Job):
        self._job = job

        # fail if this doesnt work
        self._steps_functions: List[Callable] = []
        self._init_step_functions()

        self._exception_handlers_functions: Dict[Tuple[str, type], Callable] = {}
        self._init_exception_handlers_functions()

    def _init_step_functions(self):
        """Init all"""
        self._steps_functions = [getattr(self, step, step) for step in self.steps]

        if not_implemented_steps := [step for step in self._steps_functions if not callable(step)]:
            raise JobProcessorStepNotImplementedError(
                self.__class__.__name__, *not_implemented_steps
            )

    def _init_exception_handlers_functions(self):
        """Job should be readonly"""
        self._exception_handlers_functions = {
            key: getattr(self, handler, handler) for key, handler in self.exception_handlers.items()
        }

        if not_implemented_handlers := [
            handler
            for handler in self._exception_handlers_functions.values()
            if not callable(handler)
        ]:
            raise JobProcessorHandlerNotImplementedError(
                self.__class__.__name__, *not_implemented_handlers
            )

        if not_implemented_handler_steps := [
            key[0] for key in self._exception_handlers_functions.keys() if key[0] not in self.steps
        ]:
            raise JobProcessorHandlerStepNotImplementedError(
                self.__class__.__name__, *not_implemented_handler_steps
            )

    def run(self) -> None:
        """
        Execute each step in order. If a step raises, look for a matching
        handler. The handler decides whether processing continues.
        """
        # mark job as processing
        self.on_run()

        for step_function in self._steps_functions:
            step = step_function.__name__

            try:
                self.on_step_start(step)
                step_function()
            except Exception as e:
                if exception_handler := self._lookup_handler(step, e):
                    exception_handler(e)
                else:
                    # Consider marking job as failed here since it is important to keep state correct
                    self.on_uncaught_exception(step, e)

                if self.job.state is JobStates.PROCESSING:
                    self.job.apply_state(JobStates.FAILED, reason=f"Error occurred during {step}.")

                self.job.save()
                raise

        self.job.apply_state(JobStates.SUCCEEDED)
        self.job.save()

        self.on_run_done()

    def _lookup_handler(self, step: str, e: Exception) -> Callable | None:
        """ """
        if handler := self._exception_handlers_functions.get((step, e.__class__)):
            return handler

        return None
