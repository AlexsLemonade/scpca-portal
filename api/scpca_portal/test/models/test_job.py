from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job


class TestJob(TestCase):
    def setUp(self):
        self.mock_job_id = "FAKE_JOB_ID"
        self.project_id = "FAKE_PROJECT_ID"
        self.download_config_name = "FAKE_DOWNLOAD_CONFIG"
        self.batch_job_name = f"{self.project_id}-{self.download_config_name}"
        self.project_job_batch_container_overrides = {
            "command": [
                "python",
                "manage.py",
                "generate_computed_file",
                "--project-id",
                self.project_id,
                "--download-config-name",
                self.download_config_name,
                "",
            ]
        }

    @patch("scpca_portal.models.Job._batch")
    def test_submit_job(self, mock_batch_client):
        # Set the mock return value of submit_job
        mock_batch_client.submit_job.return_value = {"jobId": self.mock_job_id}

        job = Job.get_project_job(
            project_id=self.project_id, download_config_name=self.download_config_name
        )

        # Before submission, the job instance should not have an ID
        self.assertIsNone(job.id)

        job.submit()

        mock_batch_client.submit_job.assert_called_once_with(
            jobName=self.batch_job_name,
            jobQueue=settings.AWS_BATCH_JOB_QUEUE_NAME,
            jobDefinition=settings.AWS_BATCH_JOB_DEFINITION_NAME,
            containerOverrides=self.project_job_batch_container_overrides,
        )

        # After submission, the job should be updated
        self.assertEqual(job.batch_job_id, self.mock_job_id)
        self.assertEqual(job.state, JobStates.SUBMITTED)
        self.assertIsInstance(job.submitted_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_name, self.batch_job_name)
        self.assertEqual(saved_job.batch_job_queue, settings.AWS_BATCH_JOB_QUEUE_NAME)
        self.assertEqual(saved_job.batch_job_definition, settings.AWS_BATCH_JOB_DEFINITION_NAME)
        self.assertEqual(
            saved_job.batch_container_overrides, self.project_job_batch_container_overrides
        )
        self.assertIn(self.project_id, saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.SUBMITTED)
        self.assertIsInstance(saved_job.submitted_at, datetime)
