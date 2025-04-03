from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestJob(TestCase):
    def setUp(self):
        self.mock_project_id = "SCPCP000000"
        self.mock_download_config_name = "MOCK_DOWNLOAD_CONFIG_NAME"
        self.mock_batch_job_id = "MOCK_JOB_ID"  # The job id via AWS Batch response
        self.mock_project_batch_job_name = (
            f"{self.mock_project_id}-{self.mock_download_config_name}"
        )
        self.mock_dataset = DatasetFactory()

    @patch("scpca_portal.batch.submit_job")
    def test_submit_job(self, mock_batch_submit_job):
        # Set up mock for submit_job
        mock_batch_submit_job.return_value = self.mock_batch_job_id

        job = Job.get_project_job(
            project_id=self.mock_project_id, download_config_name=self.mock_download_config_name
        )

        # Before submission, the job instance should not have an ID
        self.assertIsNone(job.id)

        job.submit()
        mock_batch_submit_job.assert_called_once()

        # After submission, the job should be updated
        self.assertEqual(job.batch_job_id, self.mock_batch_job_id)
        self.assertEqual(job.state, JobStates.SUBMITTED)
        self.assertIsInstance(job.submitted_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_id, self.mock_batch_job_id)
        self.assertEqual(saved_job.batch_job_queue, settings.AWS_BATCH_JOB_QUEUE_NAME)
        self.assertEqual(saved_job.batch_job_definition, settings.AWS_BATCH_JOB_DEFINITION_NAME)
        self.assertIn("--project-id", saved_job.batch_container_overrides["command"])
        self.assertIn(self.mock_project_id, saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.SUBMITTED)
        self.assertIsInstance(saved_job.submitted_at, datetime)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_job_failure(self, mock_batch_submit_job):
        job = JobFactory.build(batch_job_name=self.mock_project_batch_job_name)
        self.assertIsNone(job.id)  # No job created in the db yet

        # Set up mock for a failed submission
        mock_batch_submit_job.return_value = None

        success = job.submit()
        mock_batch_submit_job.assert_called_once()
        self.assertFalse(success)

        # The job state should remain default and unsaved
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(job.state, JobStates.CREATED)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job(self, mock_batch_terminate_job):
        # Job already in TERMINATED state
        terminated_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.TERMINATED,
        )

        # Should return True early without calling terminate_job
        success = terminated_job.terminate(retry_on_termination=True)
        mock_batch_terminate_job.assert_not_called()
        self.assertTrue(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED,
        )

        success = submitted_job.terminate(retry_on_termination=True)
        mock_batch_terminate_job.assert_called_once()
        self.assertTrue(success)

        # After termination, the job should be saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED)
        self.assertTrue(saved_job.retry_on_termination)
        self.assertIsInstance(saved_job.terminated_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job_failure(self, mock_batch_terminate_job):
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED,
        )

        # Set up mock for a failed termination
        mock_batch_terminate_job.return_value = False

        success = job.terminate(retry_on_termination=True)

        mock_batch_terminate_job.assert_called_once()
        self.assertFalse(success)

        saved_job = Job.objects.get(pk=job.pk)
        # The job state should remain unchanged
        self.assertEqual(saved_job.state, job.state)

    def test_get_retry_job(self):
        # Set up a non-terminated job
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            dataset=self.mock_dataset,
            state=JobStates.SUBMITTED.value,
        )

        # After execution, the call should returns None
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job)

        # Change the job state to TERMINATED
        job.state = JobStates.TERMINATED.value
        # Set up mock field values for base terminated jobs
        job.batch_job_name = "BATCH_JOB_NAME"
        job.batch_job_definition = "BATCH_JOB_DEFINITION"
        job.batch_job_queue = "BATCH_JOB_QUEUE"
        job.batch_container_overrides = "BATCH_CONTAINER_OVERRIDES"
        job.attempt = 1
        job.retry_on_termination = True

        # After execution, the call should returns a new unsaved instance for retry
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job.id)  # Should not have an ID
        # Should correctly copy the exsiting field values
        self.assertEqual(retry_job.batch_job_name, job.batch_job_name)
        self.assertEqual(retry_job.batch_job_definition, job.batch_job_definition)
        self.assertEqual(retry_job.batch_job_queue, job.batch_job_queue)
        self.assertEqual(retry_job.attempt, job.attempt + 1)

    def test_retry_jobs(self):
        # Set up mock field values for base terminated jobs
        batch_job_name = "BATCH_JOB_NAME"
        batch_job_definition = "BATCH_JOB_DEFINITION"
        batch_job_queue = "BATCH_JOB_QUEUE"
        batch_container_overrides = "BATCH_CONTAINER_OVERRIDES"
        attempt = 1
        # Set up 3 base terminated jobs for retry
        for _ in range(3):
            JobFactory(
                state=JobStates.TERMINATED.value,
                batch_job_name=batch_job_name,
                batch_job_definition=batch_job_definition,
                batch_job_queue=batch_job_queue,
                batch_container_overrides=batch_container_overrides,
                attempt=attempt,
                retry_on_termination=True,
            )

        # Before retry, there are 3 jobs in the db
        self.assertEqual(Job.objects.count(), 3)

        # After execution, the call should return a list of jobs for retry
        retry_jobs = Job.get_retry_jobs()
        self.assertNotEqual(retry_jobs, [])

        # Should be 6 jobs (base 3  + new 3) in the db
        self.assertEqual(Job.objects.count(), 6)
        # Make sure that the job is saved in the db with correct field values
        saved_retry_jobs = Job.objects.filter(state=JobStates.CREATED.value)

        for job in saved_retry_jobs:
            self.assertEqual(job.state, JobStates.CREATED.value)
            # Should correctly copy the base instance's field values
            self.assertEqual(job.batch_job_name, batch_job_name)
            self.assertEqual(job.batch_job_definition, batch_job_definition)
            self.assertEqual(job.batch_job_queue, batch_job_queue)
            self.assertEqual(job.batch_container_overrides, batch_container_overrides)
            self.assertEqual(job.attempt, 2)  # The base's attempt(1) + 1

    def test_retry_jobs_no_terminated_job_to_retry(self):
        # Set up terminated jobs with retry_on_termination set to False
        for _ in range(3):
            JobFactory(state=JobStates.SUBMITTED.value, retry_on_termination=False)

        # After execution, the call should return an empty list
        retry_jobs = Job.get_retry_jobs()
        self.assertEqual(retry_jobs, [])
