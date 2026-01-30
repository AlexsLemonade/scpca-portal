from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import JobFactory, UserDatasetFactory


class TestTerminateBatchJobs(TestCase):
    def setUp(self):
        self.terminate_batch_jobs = partial(call_command, "terminate_batch_jobs")

    def assertDatasetState(
        self,
        dataset,
        is_pending=False,
        is_processing=False,
        is_succeeded=False,
        is_failed=False,
        failed_reason=None,
        is_terminated=False,
        terminated_reason=None,
    ):
        """
        Helper for asserting the dataset state.
        """
        self.assertEqual(dataset.is_pending, is_pending)
        if is_pending:
            self.assertIsInstance(dataset.pending_at, datetime)

        self.assertEqual(dataset.is_processing, is_processing)
        if is_processing:
            self.assertIsInstance(dataset.processing_at, datetime)

        self.assertEqual(dataset.is_succeeded, is_succeeded)
        if is_succeeded:
            self.assertIsInstance(dataset.succeeded_at, datetime)

        self.assertEqual(dataset.is_failed, is_failed)
        if is_failed:
            self.assertIsInstance(dataset.failed_at, datetime)
        self.assertEqual(dataset.failed_reason, failed_reason)

        self.assertEqual(dataset.is_terminated, is_terminated)
        if is_terminated:
            self.assertIsInstance(dataset.terminated_at, datetime)
        self.assertEqual(dataset.terminated_reason, terminated_reason)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_batch_jobs(self, mock_batch_terminate_job):
        # Set up 3 PROCESSING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PROCESSING,
                dataset=UserDatasetFactory(is_processing=True),
            )
        terminated_reason = "Terminated jobs for deploy"

        # Should call terminate_job 3 times and create 3 new retry jobs
        self.terminate_batch_jobs(reason=terminated_reason, retry=True)
        self.assertEqual(mock_batch_terminate_job.call_count, 3)

        # 3 PROCESSING jobs should be updated to TERMINATED
        self.assertEqual(Job.objects.filter(state=JobStates.PROCESSING).count(), 0)
        terminate_jobs = Job.objects.filter(state=JobStates.TERMINATED)
        self.assertEqual(terminate_jobs.count(), 3)

        for terminate_job in terminate_jobs:
            self.assertEqual(terminate_job.state, JobStates.TERMINATED)
            self.assertIsInstance(terminate_job.terminated_at, datetime)
            self.assertEqual(terminate_job.terminated_reason, terminated_reason)
            self.assertDatasetState(
                terminate_job.dataset,
                is_processing=False,
                is_terminated=True,
                terminated_reason=terminate_job.terminated_reason,
            )

        # 3 new PENDING jobs should be saved in the database
        self.assertEqual(Job.objects.filter(state=JobStates.PENDING).count(), 3)

        # Set up additinoal 3 PROCESSING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PROCESSING,
                dataset=UserDatasetFactory(is_processing=True),
            )

        # Before the call, only 3 TERMINATED jobs are in the db
        self.assertEqual(Job.objects.filter(state=JobStates.TERMINATED).count(), 3)

        # Should call terminate_job 3 times without creating retry jobs
        self.terminate_batch_jobs(retry=False)
        self.assertEqual(mock_batch_terminate_job.call_count, 6)  # prev (3) + new (3)

        # After termination, 6 TERMINATED jobs should be in the db
        terminated_jobs = Job.objects.filter(state=JobStates.TERMINATED)
        self.assertEqual(terminated_jobs.count(), 6)  # prev (3) + new (3)
        # no new retry jobs should be saved in the database
        self.assertEqual(
            Job.objects.filter(state=JobStates.PENDING).count(), 3
        )  # prev (3) + new(0)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_batch_jobs_not_called(self, mock_batch_terminate_job):
        # Set up 3 SUCCEEDED jobs
        for _ in range(3):
            JobFactory(state=JobStates.SUCCEEDED, dataset=UserDatasetFactory(is_processing=False))

        # Should not call terminate_job
        self.terminate_batch_jobs()
        mock_batch_terminate_job.assert_not_called()
