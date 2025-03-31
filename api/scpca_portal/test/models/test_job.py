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

    def bulk_create_mock_jobs(self, list_of_jobs=None, num_unsaved_jobs=False):
        """Helper to create job instances using JobFactory
        If list_of_jobs, generate saved jobs for the given list.
        If num_unsaved_jobs, generate the spefified number of unsaved jobs.
        """
        if num_unsaved_jobs:
            return [
                JobFactory.build(batch_job_name=self.mock_project_batch_job_name)
                for _ in range(num_unsaved_jobs)
            ]
        else:
            return [
                JobFactory(
                    batch_job_name=self.mock_project_batch_job_name,
                    batch_job_id=job["batch_job_id"],
                    state=job["state"],
                )
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

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created(self, mock_batch_submit_job):
        # Set up 3 unsaved CREATED jobs and 3 saved jobs with different states
        mock_batch_submit_job.return_value = self.mock_batch_job_id
        unsaved_jobs = self.bulk_create_mock_jobs(num_unsaved_jobs=3)
        saved_jobs = self.bulk_create_mock_jobs(
            list_of_jobs=[
                {
                    "batch_job_id": f"{self.mock_batch_job_id}-{state}",
                    "state": state,
                }
                for state in [
                    JobStates.SUBMITTED.name,
                    JobStates.COMPLETED.name,
                    JobStates.TERMINATED.name,
                ]
            ]
        )
        jobs_to_submit = unsaved_jobs + saved_jobs

        # Before submission, there are 3 saved jobs in the db
        self.assertEqual(Job.objects.count(), 3)

        success = Job.submit_created(jobs_to_submit)
        # Should call submit_job 3 times for the unsaved jobs
        mock_batch_submit_job.assert_called()
        self.assertEqual(mock_batch_submit_job.call_count, 3)
        self.assertTrue(success)

        # After submission, the unsaved jobs should be saved with SUBMITTED state
        self.assertEqual(Job.objects.count(), 6)
        self.assertEqual(Job.objects.filter(state=JobStates.SUBMITTED.name).count(), 4)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created_no_submission(self, mock_batch_submit_job):
        # Set up 3 already saved jobs to submit
        mock_batch_submit_job.return_value = self.mock_batch_job_id
        jobs_to_submit = self.bulk_create_mock_jobs(
            list_of_jobs=[
                {
                    "batch_job_id": f"{self.mock_batch_job_id}-{i}",
                    "state": JobStates.SUBMITTED.name,
                }
                for i in range(3)
            ]
        )

        success = Job.submit_created(jobs_to_submit)
        # Should not call submit_job for already saved jobs
        mock_batch_submit_job.assert_not_called()
        self.assertTrue(success)  # No submission with no error

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

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_submitted(self, mock_batch_terminate_job):
        # Set up jobs in SUBMITTED state
        self.bulk_create_mock_jobs(
            list_of_jobs=[
                {
                    "batch_job_id": f"{self.mock_batch_job_id}-{i}",
                    "state": JobStates.SUBMITTED.name,
                }
                for i in range(3)
            ]
        )

        success = Job.terminate_submitted(retry_on_termination=True)
        # Should call submit_job 3 times for the unsaved jobs
        mock_batch_terminate_job.assert_called()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)
        self.assertTrue(success)

        # After termination, the job should be saved with correct field values
        for job in Job.objects.all():
            self.assertEqual(job.state, JobStates.TERMINATED.name)
            self.assertTrue(job.retry_on_termination)
            self.assertIsInstance(job.terminated_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_submitted_no_termination(self, mock_batch_terminate_job):
        # Set up jobs that are already TERMINATED or COMPLETED
        self.bulk_create_mock_jobs(
            list_of_jobs=[
                {
                    "batch_job_id": f"{self.mock_batch_job_id}-{state}",
                    "state": state,
                }
                for state in [JobStates.COMPLETED.name, JobStates.TERMINATED.name]
            ]
        )

        success = Job.terminate_submitted(retry_on_termination=True)
        # Should not call terminate_job for already terminated or completed jobs
        mock_batch_terminate_job.assert_not_called()
        self.assertTrue(success)  # No termination with no error

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
