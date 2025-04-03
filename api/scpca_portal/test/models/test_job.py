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
        self.assertEqual(job.state, JobStates.SUBMITTED.value)
        self.assertIsInstance(job.submitted_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_id, self.mock_batch_job_id)
        self.assertEqual(saved_job.batch_job_queue, settings.AWS_BATCH_JOB_QUEUE_NAME)
        self.assertEqual(saved_job.batch_job_definition, settings.AWS_BATCH_JOB_DEFINITION_NAME)
        self.assertIn("--project-id", saved_job.batch_container_overrides["command"])
        self.assertIn(self.mock_project_id, saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.SUBMITTED.value)
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
        self.assertEqual(job.state, JobStates.CREATED.value)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created(self, mock_batch_submit_job):
        # Set up 3 saved CREATED jobs + 3 jobs that are already submitted
        for _ in range(3):
            JobFactory(state=JobStates.CREATED.value)
        for state in [
            JobStates.SUBMITTED.value,
            JobStates.COMPLETED.value,
            JobStates.TERMINATED.value,
        ]:
            JobFactory(state=state)

        # Before submission, there are 1 job in SUBMITTED state
        self.assertEqual(Job.objects.filter(state=JobStates.SUBMITTED.value).count(), 1)

        # Should call submit_job 3 times to submit CREATED jobs
        response = Job.submit_created()
        mock_batch_submit_job.assert_called()
        self.assertEqual(mock_batch_submit_job.call_count, 3)
        self.assertNotEqual(response, [])

        # After submission, each CREATE job state should be updated to SUBMITTED
        self.assertEqual(Job.objects.filter(state=JobStates.SUBMITTED.value).count(), 4)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created_failure(self, mock_batch_submit_job):
        # Set up 3 saved CREATED jobs
        for _ in range(3):
            JobFactory(state=JobStates.CREATED.value)
        mock_batch_submit_job.return_value = []

        # Should call submit_job 3 times, each time with an exception
        response = Job.submit_created()
        mock_batch_submit_job.assert_called()
        self.assertEqual(mock_batch_submit_job.call_count, 3)
        self.assertEqual(response, [])

        # After submission, the jobs should remain unchanged
        self.assertEqual(Job.objects.filter(state=JobStates.CREATED).count(), 3)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created_no_submission(self, mock_batch_submit_job):
        # Set up already submitted jobs
        for _ in range(3):
            JobFactory(state=JobStates.SUBMITTED.value)
        mock_batch_submit_job.return_value = []

        # Should return an empty list without calling submit_job
        response = Job.submit_created()
        mock_batch_submit_job.assert_not_called()
        self.assertEqual(response, [])  # No submission with no error

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job(self, mock_batch_terminate_job):
        # Job already in TERMINATED state
        terminated_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.TERMINATED.value,
        )

        # Should return True early without calling terminate_job
        success = terminated_job.terminate(retry_on_termination=True)
        mock_batch_terminate_job.assert_not_called()
        self.assertTrue(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED.value,
        )

        success = submitted_job.terminate(retry_on_termination=True)
        mock_batch_terminate_job.assert_called_once()
        self.assertTrue(success)

        # After termination, the job should be saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED.value)
        self.assertTrue(saved_job.retry_on_termination)
        self.assertIsInstance(saved_job.terminated_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job_failure(self, mock_batch_terminate_job):
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            state=JobStates.SUBMITTED.value,
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
        # Set up 3 jobs in SUBMITTED state
        for _ in range(3):
            JobFactory(state=JobStates.SUBMITTED.value)

        # Should call terminated_job 3 times for submitted, incompleted jobs
        response = Job.terminate_submitted()
        mock_batch_terminate_job.assert_called()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)
        self.assertNotEqual(response, [])

        # After termination, the jobs should be saved with TERMINATED state
        for job in Job.objects.all():
            self.assertEqual(job.state, JobStates.TERMINATED.value)
            self.assertIsInstance(job.terminated_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_submitted_failure(self, mock_batch_terminate_job):
        # Set up mock for 3 unsuccessful terminations
        for _ in range(3):
            JobFactory(state=JobStates.SUBMITTED.value)
        mock_batch_terminate_job.return_value = []

        # Should call terminate_job 3 times, each time with an exception
        response = Job.terminate_submitted()
        mock_batch_terminate_job.assert_called()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)
        self.assertEqual(response, [])

        # After termination, the jobs should remain unchanged
        for job in Job.objects.all():
            self.assertEqual(job.state, JobStates.SUBMITTED.value)
            self.assertIsNone(job.terminated_at)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_submitted_no_termination(self, mock_batch_terminate_job):
        # Set up jobs that are already terminated or completed
        for state in [JobStates.COMPLETED.value, JobStates.TERMINATED.value]:
            JobFactory(state=state)
        mock_batch_terminate_job.return_value = []

        # Should return an empty list without calling terminate_job
        response = Job.terminate_submitted()
        mock_batch_terminate_job.assert_not_called()
        self.assertEqual(response, [])  # No termination with no error

    def test_get_retry_job(self):
        job = JobFactory(
            batch_job_name=self.mock_project_batch_job_name,
            batch_job_id=self.mock_batch_job_id,
            dataset=self.mock_dataset,
            state=JobStates.SUBMITTED.value,
        )

        # Should return None if the job state is not TERMINATED
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job)

        # Change the job state to TERMINATED
        job.state = JobStates.TERMINATED.value
        # Should return a new unsaved instance for retrying the terminated job
        retry_job = job.get_retry_job()
        self.assertIsNone(retry_job.id)  # Should not have an ID
        # Make sure required fields are copied and attempt is incremented
        self.assertEqual(retry_job.attempt, job.attempt + 1)
        self.assertEqual(retry_job.batch_job_name, job.batch_job_name)
        self.assertEqual(retry_job.batch_job_definition, job.batch_job_definition)
        self.assertEqual(retry_job.batch_job_queue, job.batch_job_queue)
