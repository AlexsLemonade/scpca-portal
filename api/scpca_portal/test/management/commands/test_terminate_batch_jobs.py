from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestTerminateBatchJobs(TestCase):
    def setUp(self):
        self.terminate_batch_jobs = partial(call_command, "terminate_batch_jobs")

    def assertDatasetState(
        self,
        dataset,
        is_processing=False,
        is_succeeded=False,
        is_failed=False,
        failed_reason=None,
        is_terminated=False,
    ):
        """
        Helper for asserting the dataset state.
        """
        self.assertEqual(dataset.is_processing, is_processing)

        self.assertEqual(dataset.is_succeeded, is_succeeded)
        if is_succeeded:
            self.assertIsInstance(dataset.processed_at, datetime)

        self.assertEqual(dataset.is_failed, is_failed)
        if is_failed:
            self.assertIsInstance(dataset.failed_at, datetime)
        self.assertEqual(dataset.failed_reason, failed_reason)

        self.assertEqual(dataset.is_terminated, is_terminated)
        if is_terminated:
            self.assertIsInstance(dataset.terminated_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_batch_jobs(self, mock_batch_terminate_job):
        # Set up 3 SUBMITTED jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.SUBMITTED,
                dataset=DatasetFactory(is_processing=True),
            )

        # Should call terminate_job 3 times
        self.terminate_batch_jobs()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)

        # SUBMITTED jobs should be updated to TERMINATED
        saved_jobs = Job.objects.all()

        for saved_job in saved_jobs:
            self.assertEqual(saved_job.state, JobStates.TERMINATED)
            self.assertIsInstance(saved_job.terminated_at, datetime)
            self.assertEqual(saved_job.terminated_reason, "Terminated SUBMITTED")
            # TODO: Assertion will fixed after update SUBMITTED (e.g., is_submitted) to PROCESSING
            self.assertDatasetState(saved_job.dataset, is_processing=True, is_terminated=True)

        # Set up additinoal 3 SUBMITTED jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.SUBMITTED,
                dataset=DatasetFactory(is_processing=True),
            )

        # Before the call, only 3 TERMINATED jobs are in the db
        self.assertEqual(Job.objects.filter(state=JobStates.TERMINATED).count(), 3)

        # Should call terminate_job 3 times (for the new jobs)
        self.terminate_batch_jobs(no_retry=False)  # Create new retry jobs
        self.assertEqual(mock_batch_terminate_job.call_count, 6)  # prev (3) + new (3)

        # After termination, 6 TERMINATED jobs should be in the db
        saved_jobs = Job.objects.filter(state=JobStates.TERMINATED)
        self.assertEqual(saved_jobs.count(), 6)  # prev (3) + new (3)
        # 3 new CREATED retry jobs should be saved in the database
        self.assertEqual(Job.objects.filter(state=JobStates.CREATED).count(), 3)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_batch_jobs_not_called(self, mock_batch_terminate_job):
        # Set up 3 SUCCEEDED jobs
        for _ in range(3):
            JobFactory(state=JobStates.SUCCEEDED, dataset=DatasetFactory(is_processing=False))

        # Should not call terminate_job
        self.terminate_batch_jobs()
        mock_batch_terminate_job.assert_not_called()
