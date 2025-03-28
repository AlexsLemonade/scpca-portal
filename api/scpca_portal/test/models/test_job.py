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
        self.aws_batch_job_status = [  # AWS Batch job statuses
            "SUBMITTED",
            "PENDING",
            "RUNNABLE",
            "STARTING",
            "RUNNING",
            "SUCCEEDED",
            "FAILED",
        ]

    def bulk_create_mock_jobs(self, list_of_jobs):
        """Helper to create job instances using JobFactory."""
        for job in list_of_jobs:
            JobFactory(
                batch_job_name=self.mock_project_batch_job_name,
                batch_job_id=job["batch_job_id"],
                state=job["state"],
            )

    def bulk_create_mock_aws_batch_jobs(self, list_of_jobs):
        """Helper to generate AWS Batch jobs for mocked method return value."""
        return [
            {
                "jobId": job["jobId"],
                "status": job["status"],
                "statusReason": f"Job {job['status']}",
            }
            for job in list_of_jobs
        ]

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

    @patch("scpca_portal.batch.get_job")
    def test_sync_state(self, mock_batch_get_job):
        # Job state is not SUBMITTED
        completed_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.COMPLETED,
        )

        # Should return False early without calling get_job
        success = completed_job.sync_state()
        mock_batch_get_job.assert_not_called()
        self.assertFalse(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED,
        )

        # Set up mock for failed get_job call
        mock_batch_get_job.return_value = False

        success = submitted_job.sync_state()
        mock_batch_get_job.assert_called()
        self.assertFalse(success)

        # The job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job, submitted_job)

        # Set up mock for get_job for RUNNING (with no state change)
        mock_batch_get_job.return_value = {
            "status": "RUNNING",
            "statusReason": "Job RUNNING",
        }

        success = submitted_job.sync_state()
        mock_batch_get_job.assert_called()
        self.assertTrue(success)

        # The job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job, submitted_job)

        # Set up mock for get_job with FAILED (with state change)
        mock_batch_get_job.return_value = {
            "status": "FAILED",
            "statusReason": "Job FAILED",
        }

        success = submitted_job.sync_state()
        mock_batch_get_job.assert_called()
        self.assertTrue(success)

        # Job should be updated and saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.COMPLETED)
        self.assertEqual(saved_job.failure_reason, mock_batch_get_job.return_value["statusReason"])

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state(self, mock_batch_get_jobs):
        # Set up mock for get_jobs with all AWS Batch job statuses
        mock_batch_get_jobs.return_value = self.bulk_create_mock_aws_batch_jobs(
            [
                {"jobId": f"{self.mock_batch_job_id}-{i}", "status": status}
                for i, status in enumerate(
                    self.aws_batch_job_status,
                )
            ]
        )
        # Jobs with SUBMITTED state
        self.bulk_create_mock_jobs(
            [
                {"batch_job_id": f"{self.mock_batch_job_id}-{i}", "state": JobStates.SUBMITTED}
                for i in range(0, 7)
            ]
        )

        success = Job.bulk_sync_state()
        mock_batch_get_jobs.assert_called_once()
        self.assertTrue(success)

        # Job with state change should be updated and saved with correct field values
        for saved_job in Job.objects.all():
            if saved_job.state != JobStates.SUBMITTED:
                # Job state should be COMPLETED
                self.assertEqual(saved_job.state, JobStates.COMPLETED)
                self.assertIn(saved_job.failure_reason, [None, "Job FAILED"])
                self.assertIsInstance(saved_job.completed_at, datetime)
            else:
                self.assertEqual(saved_job.state, JobStates.SUBMITTED)
                self.assertIsNone(saved_job.failure_reason)
                self.assertIsNone(saved_job.completed_at)

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state_no_matching_batch_job_found(self, mock_batch_get_jobs):
        # Set up mock for get_jobs with no matched AWS job found
        mock_batch_get_jobs.return_value = self.bulk_create_mock_aws_batch_jobs(
            [
                {"jobId": f"{self.mock_batch_job_id}-{i}", "status": status}
                for i, status in enumerate(["PENDING", "FAILED"])
            ]
        )
        self.bulk_create_mock_jobs(
            [
                {"batch_job_id": f"{self.mock_batch_job_id}-{i}", "state": JobStates.SUBMITTED}
                for i in range(1, 4)
            ]
        )

        # A missing batch job should not interrupt the remaining jobs
        success = Job.bulk_sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)

        # Job with state change should be updated and saved with correct field values
        saved_job = Job.objects.filter(batch_job_id=f"{self.mock_batch_job_id}-{1}").first()
        self.assertEqual(saved_job.state, JobStates.COMPLETED)
        self.assertEqual(saved_job.failure_reason, "Job FAILED")
        self.assertIsInstance(saved_job.completed_at, datetime)

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
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            dataset=self.mock_dataset,
            state=JobStates.SUBMITTED,
        )

        # Should return None if the job state is not TERMINATED
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job)

        # Change the job state to TERMINATED
        job.state = JobStates.TERMINATED
        # Should return a new unsaved instance for retrying the terminated job
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job.id)  # Should not have an ID
        # Make sure required fields are copied and attempt is incremented
        self.assertEqual(retry_job.attempt, job.attempt + 1)
        self.assertEqual(retry_job.batch_job_name, job.batch_job_name)
        self.assertEqual(retry_job.batch_job_definition, job.batch_job_definition)
        self.assertEqual(retry_job.batch_job_queue, job.batch_job_queue)
