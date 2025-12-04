# from unittest.mock import patch

# from django.conf import settings
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.exceptions import (
    JobProcessorHandlerNotImplementedError,
    JobProcessorHandlerStepNotImplementedError,
    JobProcessorStepNotImplementedError,
)
from scpca_portal.job_processors import JobProcessorABC
from scpca_portal.test.factories import JobFactory


class TestJobProcessorABC(TestCase):

    def test_job_processor_success(self):
        class TestProcessor(JobProcessorABC):
            test_order = []

            steps = ["step_one", "step_two"]
            exception_handlers = {}

            def step_one(self):
                self.test_order.append("step_one")

            def step_two(self):
                self.test_order.append("step_two")

        job = JobFactory(state=JobStates.PROCESSING)

        processor = TestProcessor(job)
        processor.run()

        self.assertEqual(processor.test_order, ["step_one", "step_two"])
        self.assertEqual(processor.job.state, JobStates.SUCCEEDED)

    def test_job_processor_processor_step_not_implemented_error(self):
        class TestProcessor(JobProcessorABC):
            steps = ["step_one", "step_two"]
            exception_handlers = {}

        job = JobFactory(state=JobStates.PROCESSING)

        with self.assertRaises(JobProcessorStepNotImplementedError):
            TestProcessor(job)

    def test_job_processor_handler_not_implemented_error(self):
        # The handler is not implmeneted
        class TestProcessor(JobProcessorABC):
            steps = ["step_one"]
            exception_handlers = {("step_one", Exception): "not_implemented"}

            def step_one(self):
                pass

        job = JobFactory(state=JobStates.PROCESSING)

        with self.assertRaises(JobProcessorHandlerNotImplementedError):
            TestProcessor(job)

    def test_job_processor_undefined_handler_steps_error(self):
        class TestProcessor(JobProcessorABC):
            steps = ["step_one"]
            exception_handlers = {}
            exception_handlers = {("not_implemented", Exception): "handle_step_one"}

            def step_one(self):
                pass

            def handle_step_one(self):
                pass

        job = JobFactory(state=JobStates.PROCESSING)

        with self.assertRaises(JobProcessorHandlerStepNotImplementedError):
            TestProcessor(job)

    def test_job_processor_uncaught_error(self):
        # Assert that an uncaught error will bubble out of the processor
        # And the job is correctly marked as failed
        class TestProcessor(JobProcessorABC):
            steps = ["step_one", "step_two"]
            exception_handlers = {}

            def step_one(self):
                pass

            def step_two(self):
                raise KeyError

        job = JobFactory(state=JobStates.PROCESSING)

        processor = TestProcessor(job)

        with self.assertRaises(KeyError):
            processor.run()

        self.assertEqual(processor.job.state, JobStates.FAILED)

    def test_job_processor_caught_error(self):
        class TestProcessor(JobProcessorABC):

            steps = ["step_one", "step_two"]
            exception_handlers = {("step_two", KeyError): "handle_step_two_keyerror"}

            def step_one(self):
                pass

            def step_two(self):
                raise KeyError

            def handle_step_two_keyerror(self, e: Exception):
                self.job.apply_state(JobStates.FAILED, reason="Caught Error")
                self.job.save()

        job = JobFactory(state=JobStates.PROCESSING)

        processor = TestProcessor(job)

        with self.assertRaises(KeyError):
            processor.run()

        self.assertEqual(processor.job.state, JobStates.FAILED)
        self.assertEqual(processor.job.failed_reason, "Caught Error")
