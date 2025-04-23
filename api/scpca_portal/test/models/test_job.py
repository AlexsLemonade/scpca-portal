from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestJob(TestCase):
    def assert_dataset(self, dataset, is_processing, is_errored, errored_at, error_message):
        """
        Helper for asserting the dataset state.
        """
        self.assertEqual(dataset.is_processing, is_processing)
        self.assertEqual(dataset.is_errored, is_errored)

        if errored_at:
            self.assertIsInstance(dataset.errored_at, datetime)
        else:
            self.assertEqual(dataset.errored_at, errored_at)

        self.assertEqual(dataset.error_message, error_message)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_job(self, mock_batch_submit_job):
        # Set up mock for submit_job
        mock_batch_job_id = "MOCK_JOB_ID"  # The job id returned via AWS Batch response
        mock_batch_submit_job.return_value = mock_batch_job_id
        project_id = "SCPCP000000"

        job = Job.get_project_job(
            project_id=project_id,
            download_config_name="MOCK_DOWNLOAD_CONFIG_NAME",
        )

        # Before submission, the job instance should not have an ID
        self.assertIsNone(job.id)

        job.submit()
        mock_batch_submit_job.assert_called_once()

        # After submission, the job should be updated
        self.assertEqual(job.batch_job_id, mock_batch_job_id)
        self.assertEqual(job.state, JobStates.SUBMITTED.value)
        self.assertIsInstance(job.submitted_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_id, mock_batch_job_id)
        self.assertEqual(saved_job.batch_job_queue, settings.AWS_BATCH_JOB_QUEUE_NAME)
        self.assertEqual(saved_job.batch_job_definition, settings.AWS_BATCH_JOB_DEFINITION_NAME)
        self.assertIn("--project-id", saved_job.batch_container_overrides["command"])
        self.assertIn(project_id, saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.SUBMITTED.value)
        self.assertIsInstance(saved_job.submitted_at, datetime)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_job_failure(self, mock_batch_submit_job):
        job = JobFactory.build()
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

    @patch("scpca_portal.batch.get_jobs")
    def test_sync_state(self, mock_batch_get_jobs):
        # Job state is not SUBMITTED
        completed_job = JobFactory(state=JobStates.COMPLETED, dataset=DatasetFactory())

        # Should return False early without calling get_jobs
        success = completed_job.sync_state()
        mock_batch_get_jobs.assert_not_called()
        self.assertFalse(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(
            state=JobStates.SUBMITTED, dataset=DatasetFactory(is_processing=True)
        )

        # Set up mock for failed get_jobs call
        mock_batch_get_jobs.return_value = False

        success = submitted_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertFalse(success)

        # The job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job, submitted_job)

        # Set up mock for get_jobs for RUNNING
        mock_batch_get_jobs.return_value = [
            {
                "status": "RUNNING",
                "statusReason": "Job RUNNING",
            }
        ]

        success = submitted_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertFalse(success)  # Synced but no update in the db

        # The job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job, submitted_job)

        # Set up mock for get_jobs with TERMINATED
        mock_batch_get_jobs.return_value = [
            {
                "status": "FAILED",
                "statusReason": "Job FAILED",
                "isTerminated": True,
            }
        ]

        success = submitted_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)  # Synced and updated the db

        # Job should be updated and saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED)
        self.assertIsInstance(saved_job.terminated_at, datetime)
        self.assertIsNone(saved_job.failure_reason)
        self.assert_dataset(
            saved_job.dataset,
            is_processing=False,
            is_errored=False,
            errored_at=None,
            error_message=None,
        )

        # Set up mock for get_jobs with FAILED
        submitted_job.state = JobStates.SUBMITTED

        mock_batch_get_jobs.return_value = [
            {
                "status": "FAILED",
                "statusReason": "Job FAILED",
            }
        ]

        success = submitted_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)  # Synced and updated the db

        # Job should be updated and saved with correct field values
        saved_job = Job.objects.get(pk=submitted_job.pk)
        self.assertEqual(saved_job.state, JobStates.COMPLETED)
        self.assertEqual(saved_job.failure_reason, "Job FAILED")
        self.assertIsInstance(saved_job.completed_at, datetime)
        self.assert_dataset(
            saved_job.dataset,
            is_processing=False,
            is_errored=True,
            errored_at=saved_job.dataset.errored_at,
            error_message=saved_job.failure_reason,
        )

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state(self, mock_batch_get_jobs):
        # Set up mock for get_jobs
        jobs_to_sync = [
            JobFactory(state=JobStates.SUBMITTED, dataset=DatasetFactory(is_processing=True))
            for _ in range(8)
        ]
        mock_response = [{"jobId": job.batch_job_id} for job in jobs_to_sync]
        # All AWS Batch job statuses (7) + FAILED and terminated job (1)
        mock_response[0]["status"] = "SUBMITTED"
        mock_response[1]["status"] = "PENDING"
        mock_response[2]["status"] = "RUNNABLE"
        mock_response[3]["status"] = "STARTING"
        mock_response[4]["status"] = "RUNNING"
        mock_response[5]["status"] = "SUCCEEDED"
        mock_response[6]["status"] = "FAILED"
        mock_response[7]["status"] = "FAILED"
        mock_response[7]["isTerminated"] = True
        mock_response = [{**job, "statusReason": f"Job {job['status']}"} for job in mock_response]
        mock_batch_get_jobs.return_value = mock_response

        success = Job.bulk_sync_state()
        mock_batch_get_jobs.assert_called_once()
        self.assertTrue(success)

        # After synchronization, all jobs should be saved with correct field values
        completed_jobs = Job.objects.filter(state=JobStates.COMPLETED)
        terminated_jobs = Job.objects.filter(state=JobStates.TERMINATED)
        submitted_jobs = Job.objects.exclude(state__in=[JobStates.COMPLETED, JobStates.TERMINATED])

        for completed_job in completed_jobs:
            if completed_job.failure_reason:
                self.assert_dataset(
                    completed_job.dataset,
                    is_processing=False,
                    is_errored=True,
                    errored_at=completed_job.dataset.errored_at,
                    error_message=completed_job.failure_reason,
                )
            else:
                self.assert_dataset(
                    completed_job.dataset,
                    is_processing=False,
                    is_errored=False,
                    errored_at=None,
                    error_message=None,
                )

        for terminated_job in terminated_jobs:
            self.assertIsNone(terminated_job.failure_reason)
            self.assertIsInstance(terminated_job.terminated_at, datetime)
            self.assert_dataset(
                terminated_job.dataset,
                is_processing=False,
                is_errored=False,
                errored_at=None,
                error_message=None,
            )

        for submitted_job in submitted_jobs:
            self.assertIsNone(submitted_job.failure_reason)
            self.assertIsNone(submitted_job.completed_at)
            self.assertIsNone(submitted_job.terminated_at)
            self.assert_dataset(
                submitted_job.dataset,
                is_processing=True,
                is_errored=False,
                errored_at=None,
                error_message=None,
            )

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state_no_matching_batch_job_found(self, mock_batch_get_jobs):
        # Set up mock for get_jobs with no matched AWS job found
        jobs_to_sync = [
            JobFactory(state=JobStates.SUBMITTED, dataset=DatasetFactory(is_processing=True))
            for _ in range(4)
        ]
        mock_response = [
            {
                "jobId": jobs_to_sync[2].batch_job_id,
                "status": "FAILED",
                "statusReason": "Job FAILED",
            }
        ]
        mock_batch_get_jobs.return_value = mock_response

        # A missing batch job should not interrupt the remaining jobs
        success = Job.bulk_sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)

        # Job with state change should be updated and saved with correct field values
        saved_job = Job.objects.filter(batch_job_id=jobs_to_sync[2].batch_job_id).first()
        self.assertEqual(saved_job.state, JobStates.COMPLETED)
        self.assertEqual(saved_job.failure_reason, "Job FAILED")
        self.assertIsInstance(saved_job.completed_at, datetime)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job(self, mock_batch_terminate_job):
        # Job already in TERMINATED state
        terminated_job = JobFactory(state=JobStates.TERMINATED.value)

        # Should return True early without calling terminate_job
        success = terminated_job.terminate(retry_on_termination=True)
        mock_batch_terminate_job.assert_not_called()
        self.assertTrue(success)

        # Job is in SUBMITTED state
        submitted_job = JobFactory(state=JobStates.SUBMITTED.value)

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
        job = JobFactory(state=JobStates.SUBMITTED.value)

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
        # Set up a non-terminated job
        job = JobFactory(
            dataset=DatasetFactory(),
            state=JobStates.SUBMITTED.value,
        )

        # After execution, the call should returns None
        retry_job = job.get_retry_job()
        self.assertFalse(retry_job)

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

    def test_create_terminated_retry_jobs(self):
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
        retry_jobs = Job.create_terminated_retry_jobs()
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

    def test_create_terminated_retry_jobs_no_terminated_job_to_retry(self):
        # Set up terminated jobs with retry_on_termination set to False
        for _ in range(3):
            JobFactory(state=JobStates.SUBMITTED.value, retry_on_termination=False)

        # After execution, the call should return an empty list
        retry_jobs = Job.create_terminated_retry_jobs()
        self.assertEqual(retry_jobs, [])
