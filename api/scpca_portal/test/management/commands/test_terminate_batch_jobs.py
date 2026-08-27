from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums import DatasetStates, JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import CCDLDatasetFactory, JobFactory


class TestTerminateBatchJobs(TestCase):
    def setUp(self):
        self.terminate_batch_jobs = partial(call_command, "terminate_batch_jobs")

    def assertDatasetState(self, dataset, job_state):
        """
        Helper for asserting the dataset state.
        """
        if job_state in [JobStates.PENDING, JobStates.PROCESSING]:
            self.assertEqual(dataset.state, DatasetStates.PROCESSING)

        if job_state == JobStates.SUCCEEDED:
            self.assertEqual(dataset.state, DatasetStates.SUCCEEDED)

        if job_state in [JobStates.FAILED, JobStates.TERMINATED]:
            self.assertEqual(dataset.state, DatasetStates.FAILED)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_batch_jobs(self, mock_batch_terminate_job):
        # Set up 3 PROCESSING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PROCESSING,
                dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING),
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
            terminate_job.save()
            self.assertEqual(terminate_job.state, JobStates.TERMINATED)
            self.assertIsInstance(terminate_job.terminated_at, datetime)
            self.assertEqual(terminate_job.terminated_reason, terminated_reason)
            # Dataset should sync with the new retry job (latest job)
            self.assertDatasetState(terminate_job.dataset, JobStates.PENDING)

        # 3 new PENDING jobs should be saved in the database
        self.assertEqual(Job.objects.filter(state=JobStates.PENDING).count(), 3)

        # Set up additional 3 PROCESSING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PROCESSING,
                dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING),
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
            JobFactory(
                state=JobStates.SUCCEEDED, dataset=CCDLDatasetFactory(state=DatasetStates.SUCCEEDED)
            )

        # Should not call terminate_job
        self.terminate_batch_jobs()
        mock_batch_terminate_job.assert_not_called()
