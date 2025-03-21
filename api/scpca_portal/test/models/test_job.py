from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import JobFactory


class TestJob(TestCase):
    def setUp(self):
        self.mock_project_id = "SCPCP000000"
        self.mock_download_config_name = "MOCK_DOWNLOAD_CONFIG_NAME"
        self.mock_batch_job_id = "MOCK_JOB_ID"  # The job id via AWS Batch response
        self.mock_project_batch_job_name = (
            f"{self.mock_project_id}-{self.mock_download_config_name}"
        )

    @patch("scpca_portal.models.Job._batch")
    def test_submit_job(self, mock_batch_client):
        # Set up mock for submit_job
        mock_batch_client.submit_job.return_value = {"jobId": self.mock_batch_job_id}

        job = Job.get_project_job(
            project_id=self.mock_project_id, download_config_name=self.mock_download_config_name
        )

        # Before submission, the job instance should not have an ID
        self.assertIsNone(job.id)

        job.submit()
        mock_batch_client.submit_job.assert_called_once()

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

    @patch("scpca_portal.models.Job._batch")
    def test_terminate_job(self, mock_batch_client):
        # Job already in TERMINATED state
        terminated_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.TERMINATED,
        )

        # Should return True early without calling terminate_job
        success = terminated_job.terminate(retry_on_termination=True)
        mock_batch_client.terminate_job.assert_not_called()
        self.assertTrue(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED,
        )

        success = submitted_job.terminate(retry_on_termination=True)
        mock_batch_client.terminate_job.assert_called_once()
        self.assertTrue(success)

        # After termination, the job should be saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED)
        self.assertTrue(saved_job.retry_on_termination)
        self.assertIsInstance(saved_job.terminated_at, datetime)

    @patch("scpca_portal.models.Job._batch")
    def test_terminate_job_failure(self, mock_batch_client):
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED,
        )

        # Set up mock to raise an exception
        mock_batch_client.terminate_job.side_effect = Exception("Exception")

        success = job.terminate(retry_on_termination=True)
        mock_batch_client.terminate_job.assert_called_once()
        self.assertFalse(success)

        saved_job = Job.objects.get(pk=job.pk)
        # The job state should remain unchanged
        self.assertEqual(saved_job.state, job.state)
