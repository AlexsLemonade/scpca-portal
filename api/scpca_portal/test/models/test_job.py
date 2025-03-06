from datetime import datetime
from unittest.mock import patch

from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job


class TestJob(TestCase):
    def setUp(self):
        self.mock_job_id = "FAKE_JOB_ID"
        self.resource_id = "FAKE_RESOURCE_ID"
        self.batch_job_name = "FAKE_JOB_NAME"
        self.batch_job_queue = "FAKE_JOB_QUEUE"
        self.batch_job_definition = "FAKE_JOB_DEFINITION"
        self.batch_container_overrides = {
            "command": ["FAKE_COMMAND"],
        }

    @patch("scpca_portal.models.Job._batch")
    def test_submit_job(self, mock_batch_client):
        # Set the mock return value of submit_job
        mock_batch_client.submit_job.return_value = {"jobId": self.mock_job_id}

        job = Job.get_job(
            batch_job_name=self.batch_job_name,
            batch_job_queue=self.batch_job_queue,
            batch_job_definition=self.batch_job_definition,
            batch_container_overrides=self.batch_container_overrides,
        )

        # Before submission, the job instance should not have an ID
        self.assertIsNone(job.id)

        job.submit(resource_id=self.resource_id)

        mock_batch_client.submit_job.assert_called_once_with(
            jobName=self.batch_job_name,
            jobQueue=self.batch_job_queue,
            jobDefinition=self.batch_job_definition,
            containerOverrides=self.batch_container_overrides,
        )

        # After submission, the job should be updated
        self.assertEqual(job.batch_job_id, self.mock_job_id)
        self.assertEqual(job.state, JobStates.SUBMITTED)
        self.assertIsInstance(job.submitted_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_name, self.batch_job_name)
        self.assertEqual(saved_job.batch_job_queue, self.batch_job_queue)
        self.assertEqual(saved_job.batch_job_definition, self.batch_job_definition)
        self.assertEqual(saved_job.batch_container_overrides, self.batch_container_overrides)
        self.assertIn(self.resource_id, saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.SUBMITTED)
        self.assertIsInstance(saved_job.submitted_at, datetime)
