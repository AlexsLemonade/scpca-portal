from datetime import datetime
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.test import TestCase

from scpca_portal import common
from scpca_portal.enums import JobStates
from scpca_portal.models import Dataset, Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestJob(TestCase):
    def assertDatasetState(
        self,
        dataset,
        is_pending=False,
        is_processing=False,
        is_succeeded=False,
        is_failed=False,
        failed_reason=None,
        is_terminated=False,
        terminated_reason=None,
    ):
        """
        Helper for asserting the dataset state.
        """
        self.assertEqual(dataset.is_pending, is_pending)
        if is_pending:
            self.assertIsInstance(dataset.pending_at, datetime)

        self.assertEqual(dataset.is_processing, is_processing)
        if is_processing:
            self.assertIsInstance(dataset.processing_at, datetime)

        self.assertEqual(dataset.is_succeeded, is_succeeded)
        if is_succeeded:
            self.assertIsInstance(dataset.succeeded_at, datetime)

        self.assertEqual(dataset.is_failed, is_failed)
        if is_failed:
            self.assertIsInstance(dataset.failed_at, datetime)
        self.assertEqual(dataset.failed_reason, failed_reason)

        self.assertEqual(dataset.is_terminated, is_terminated)
        if is_terminated:
            self.assertIsInstance(dataset.terminated_at, datetime)
        self.assertEqual(dataset.terminated_reason, terminated_reason)

    def test_apply_state(self):
        job = JobFactory(state=JobStates.PENDING, dataset=DatasetFactory())

        # Update the state to PROCESSING
        job.apply_state(JobStates.PROCESSING)
        self.assertEqual(job.state, JobStates.PROCESSING)
        self.assertIsInstance(job.processing_at, datetime)
        self.assertDatasetState(job.dataset, is_pending=False, is_processing=True)

        # Update the state to SUCEEDED
        job.apply_state(JobStates.SUCCEEDED)
        self.assertEqual(job.state, JobStates.SUCCEEDED)
        self.assertIsInstance(job.succeeded_at, datetime)
        self.assertDatasetState(job.dataset, is_processing=False, is_succeeded=True)

        # Update the state to FAILED
        failed_reason = f"Job {JobStates.FAILED}"
        job.apply_state(JobStates.FAILED, failed_reason)
        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, failed_reason)
        self.assertIsInstance(job.failed_at, datetime)
        self.assertDatasetState(
            job.dataset,
            is_succeeded=False,
            is_failed=True,
            failed_reason=failed_reason,
        )

        # Update the state to TERMINATED
        terminated_reason = f"Job {JobStates.TERMINATED}"
        job.apply_state(JobStates.TERMINATED, terminated_reason)
        self.assertEqual(job.state, JobStates.TERMINATED)
        self.assertEqual(job.terminated_reason, terminated_reason)
        self.assertIsInstance(job.terminated_at, datetime)
        self.assertDatasetState(
            job.dataset,
            is_failed=False,
            failed_reason=None,
            is_terminated=True,
            terminated_reason=terminated_reason,
        )

    @patch(
        "scpca_portal.models.dataset.Dataset.has_lockfile_projects",
        new_callable=PropertyMock,
        return_value=[],
    )
    @patch("scpca_portal.batch.submit_job")
    def test_submit(self, mock_batch_submit_job, _):
        # Set up mock for submit_job
        mock_batch_job_id = "MOCK_JOB_ID"  # The job id returned via AWS Batch response
        mock_batch_submit_job.return_value = mock_batch_job_id

        dataset = DatasetFactory(is_processing=False)
        job = Job.get_dataset_job(dataset)
        job.dataset = dataset

        job.submit()
        mock_batch_submit_job.assert_called_once()

        # After submission, the job should be updated
        self.assertEqual(job.batch_job_id, mock_batch_job_id)
        self.assertEqual(job.state, JobStates.PROCESSING)
        self.assertIsInstance(job.processing_at, datetime)

        # Make sure that the job is saved in the db with correct field values
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.batch_job_id, mock_batch_job_id)
        self.assertEqual(saved_job.batch_job_queue, settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME)
        self.assertEqual(
            saved_job.batch_job_definition, settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
        )
        self.assertIn("--job-id", saved_job.batch_container_overrides["command"])
        self.assertIn(str(job.id), saved_job.batch_container_overrides["command"])
        self.assertEqual(saved_job.state, JobStates.PROCESSING)
        self.assertIsInstance(saved_job.processing_at, datetime)

    @patch("scpca_portal.models.dataset.Dataset.has_locked_projects", new_callable=PropertyMock)
    @patch("scpca_portal.models.dataset.Dataset.has_lockfile_projects", new_callable=PropertyMock)
    @patch("scpca_portal.batch.submit_job")
    def test_submit_handle_exceptions(
        self, mock_batch_submit_job, mock_has_lockfile_projects, mock_has_locked_projects
    ):
        # Set default mock return values
        mock_batch_submit_job.return_value = "MOCK_JOB_ID"
        mock_has_lockfile_projects.return_value = False
        mock_has_locked_projects.return_value = False

        # Assert "Job is not in a pending state" exception thrown correctly
        non_pending_job = JobFactory(
            state=JobStates.SUCCEEDED, dataset=DatasetFactory(is_processing=False)
        )
        with self.assertRaises(Exception) as e:
            non_pending_job.submit()
        self.assertEqual(str(e.exception), "Job is not in a pending state.")

        # Assert "Dataset has a locked project" exception thrown correctly
        dataset = DatasetFactory(is_processing=False)
        job = Job.get_dataset_job(dataset)
        job.dataset = dataset

        mock_has_lockfile_projects.return_value = True
        mock_has_locked_projects.return_value = False
        with self.assertRaises(Exception) as e:
            job.submit()
        self.assertEqual(str(e.exception), "Dataset has a locked project.")

        mock_has_lockfile_projects.return_value = False
        mock_has_locked_projects.return_value = True
        with self.assertRaises(Exception) as e:
            job.submit()
        self.assertEqual(str(e.exception), "Dataset has a locked project.")

        mock_has_lockfile_projects.return_value = False
        mock_has_locked_projects.return_value = False

        # Assert "Error submitting job to Batch." exception thrown correctly
        mock_batch_submit_job.return_value = None
        with self.assertRaises(Exception) as e:
            job.submit()
        self.assertEqual(str(e.exception), "Error submitting job to Batch.")

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending(self, mock_batch_submit_job):
        # Set up 3 saved PENDING jobs + 4 jobs that are either processing or in the final states
        for _ in range(3):
            JobFactory(
                state=JobStates.PENDING,
                dataset=DatasetFactory(is_pending=True, is_processing=False),
            )
        for state in common.SUBMITTED_JOB_STATES:
            JobFactory(state=state, dataset=DatasetFactory(is_pending=False, is_processing=False))

        # Before submission, there are 1 job in PROCESSING state
        self.assertEqual(Job.objects.filter(state=JobStates.PROCESSING).count(), 1)
        mock_batch_submit_job.return_value = "MOCK_JOB_ID"

        # Should call submit_job 3 times to submit PENDING jobs
        with patch(
            "scpca_portal.models.dataset.Dataset.has_lockfile_projects",
            new_callable=PropertyMock,
            return_value=[],
        ):
            response = Job.submit_pending()
        mock_batch_submit_job.assert_called()
        self.assertEqual(mock_batch_submit_job.call_count, 3)
        self.assertNotEqual(response, [])

        # After submission, each PENDING job state should be updated to PROCESSING
        self.assertEqual(Job.objects.filter(state=JobStates.PROCESSING).count(), 4)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending_failure(self, mock_batch_submit_job):
        # Set up 3 saved PENDING jobs
        for _ in range(3):
            JobFactory(state=JobStates.PENDING, dataset=DatasetFactory(is_pending=False))
        mock_batch_submit_job.return_value = []

        # Should call submit_job 3 times, each time with an exception
        with patch(
            "scpca_portal.models.dataset.Dataset.has_lockfile_projects",
            new_callable=PropertyMock,
            return_value=[],
        ):
            response = Job.submit_pending()
        mock_batch_submit_job.assert_called()
        self.assertEqual(mock_batch_submit_job.call_count, 3)
        self.assertEqual(response, [])

        # After submission, the jobs should remain unchanged
        self.assertEqual(Job.objects.filter(state=JobStates.PENDING).count(), 3)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending_no_submission(self, mock_batch_submit_job):
        # Set up already submitted jobs
        for _ in range(3):
            JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))
        mock_batch_submit_job.return_value = []

        # Should return an empty list without calling submit_job
        response = Job.submit_pending()
        mock_batch_submit_job.assert_not_called()
        self.assertEqual(response, [])  # No submission with no error

    @patch("scpca_portal.batch.get_jobs")
    def test_sync_state(self, mock_batch_get_jobs):
        # Job state is not PROCESSING
        succeeded_job = JobFactory(state=JobStates.SUCCEEDED, dataset=DatasetFactory())

        # Should return False early without calling get_jobs
        success = succeeded_job.sync_state()
        mock_batch_get_jobs.assert_not_called()
        self.assertFalse(success)

        # Job is in PROCESSING state
        processing_job = JobFactory(
            state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True)
        )

        # Set up mock for get_jobs call
        mock_batch_get_jobs.return_value = False

        success = processing_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertFalse(success)  # Synced but no update in the db

        # Job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=processing_job.pk)
        self.assertEqual(saved_job, processing_job)

        # Set up mock for get_jobs for 'RUNNING'
        mock_batch_get_jobs.return_value = [
            {
                "status": "RUNNING",
                "statusReason": "Job RUNNING",
            }
        ]

        success = processing_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertFalse(success)  # Synced but no update in the db

        # Job should remain unchanged and unsaved
        saved_job = Job.objects.get(pk=processing_job.pk)
        self.assertEqual(saved_job, processing_job)

        # Set up mock for get_jobs with'TERMINATED'
        mock_batch_get_jobs.return_value = [
            {
                "status": "FAILED",
                "statusReason": "Job TERMINATED",
                "isTerminated": True,
            }
        ]

        success = processing_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)  # Synced and updated the db

        # Job should be updated and saved with correct field values
        saved_job = Job.objects.get(pk=processing_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED)
        self.assertIsInstance(saved_job.terminated_at, datetime)
        self.assertEqual(saved_job.terminated_reason, "Job TERMINATED")
        saved_job.dataset.update_from_last_job()  # Sync the associated dataset
        self.assertDatasetState(
            saved_job.dataset,
            is_processing=False,
            is_terminated=True,
            terminated_reason=saved_job.terminated_reason,
        )

        # Job is in PROCESSING state
        processing_job = JobFactory(
            state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True)
        )
        # Set up mock for get_jobs with 'FAILED'
        mock_batch_get_jobs.return_value = [
            {
                "status": "FAILED",
                "statusReason": "Job FAILED",
            }
        ]

        success = processing_job.sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)  # Synced and updated the db

        # Job should be updated and saved with correct field values
        saved_job = Job.objects.get(pk=processing_job.pk)
        self.assertEqual(saved_job.state, JobStates.FAILED)
        self.assertEqual(saved_job.failed_reason, "Job FAILED")
        self.assertIsInstance(saved_job.failed_at, datetime)
        saved_job.dataset.update_from_last_job()  # Sync the associated dataset
        self.assertDatasetState(
            saved_job.dataset,
            is_processing=False,
            is_failed=True,
            failed_reason=saved_job.failed_reason,
        )

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state(self, mock_batch_get_jobs):
        # Set up mock for get_jobs
        jobs_to_sync = [
            JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))
            for _ in range(8)
        ]
        mock_response = [{"jobId": job.batch_job_id} for job in jobs_to_sync]
        # All AWS Batch job statuses (7) + FAILED & terminated job (1)
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
        processing_jobs = Job.objects.filter(state=JobStates.PROCESSING)
        succeeded_jobs = Job.objects.filter(state=JobStates.SUCCEEDED)
        failed_jobs = Job.objects.filter(state=JobStates.FAILED)
        terminated_jobs = Job.objects.filter(state=JobStates.TERMINATED)

        # PROCESSING jobs should not be updated
        for processing_job in processing_jobs:
            processing_job.dataset.update_from_last_job()  # Sync the associated dataset
            self.assertDatasetState(processing_job.dataset, is_processing=True)

        # SUCCEEDED jobs should be updated
        for succeeded_job in succeeded_jobs:
            self.assertIsNone(processing_job.failed_reason)
            self.assertIsInstance(succeeded_job.succeeded_at, datetime)
            succeeded_job.dataset.update_from_last_job()  # Sync the associated dataset state
            self.assertDatasetState(succeeded_job.dataset, is_processing=False, is_succeeded=True)

        # FAILED jobs should be updated
        for failed_job in failed_jobs:
            self.assertEqual(failed_job.failed_reason, "Job FAILED")
            self.assertIsInstance(failed_job.failed_at, datetime)
            failed_job.dataset.update_from_last_job()  # Sync the associated dataset state
            self.assertDatasetState(
                failed_job.dataset,
                is_processing=False,
                is_failed=True,
                failed_reason=failed_job.failed_reason,
            )

        # TERMINATED jobs should be updated
        for terminated_job in terminated_jobs:
            self.assertEqual(terminated_job.failed_reason, "Job FAILED")
            self.assertIsInstance(terminated_job.terminated_at, datetime)
            terminated_job.dataset.update_from_last_job()  # Sync the associated dataset state
            self.assertDatasetState(
                terminated_job.dataset,
                is_processing=False,
                is_terminated=True,
                terminated_reason=terminated_job.terminated_reason,
            )

    @patch("scpca_portal.batch.get_jobs")
    def test_bulk_sync_state_no_matching_batch_job_found(self, mock_batch_get_jobs):
        # Set up mock for get_jobs with no matched AWS job found
        jobs_to_sync = [
            JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))
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

        # A missing batch job should not interrupt the syncing process
        success = Job.bulk_sync_state()
        mock_batch_get_jobs.assert_called()
        self.assertTrue(success)

        # Job with state change should be updated and saved with correct field values
        saved_job = Job.objects.filter(batch_job_id=jobs_to_sync[2].batch_job_id).first()
        self.assertEqual(saved_job.state, JobStates.FAILED)
        self.assertEqual(saved_job.failed_reason, "Job FAILED")
        self.assertIsInstance(saved_job.failed_at, datetime)
        saved_job.dataset.update_from_last_job()  # Sync the associated dataset state
        self.assertDatasetState(
            saved_job.dataset,
            is_processing=False,
            is_failed=True,
            failed_reason=saved_job.failed_reason,
        )

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job(self, mock_batch_terminate_job):
        # Job already in TERMINATED state
        terminated_job = JobFactory(
            state=JobStates.TERMINATED, dataset=DatasetFactory(is_terminated=True)
        )

        # Should return True early without calling terminate_job
        success = terminated_job.terminate()
        mock_batch_terminate_job.assert_not_called()
        self.assertTrue(success)

        # Job is in PROCESSING state
        processing_job = JobFactory(
            state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True)
        )

        success = processing_job.terminate()
        mock_batch_terminate_job.assert_called_once()
        self.assertTrue(success)

        # After termination, the job should be saved with correct field values
        saved_job = Job.objects.get(pk=processing_job.pk)
        self.assertEqual(saved_job.state, JobStates.TERMINATED)
        self.assertIsInstance(saved_job.terminated_at, datetime)
        saved_job.dataset.update_from_last_job()  # Sync the associated dataset
        self.assertDatasetState(
            saved_job.dataset,
            is_processing=False,
            is_terminated=True,
            terminated_reason=saved_job.terminated_reason,
        )

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_job_failure(self, mock_batch_terminate_job):
        job = JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))

        # Set up mock for a failed termination
        mock_batch_terminate_job.return_value = False

        success = job.terminate()
        mock_batch_terminate_job.assert_called_once()
        self.assertFalse(success)

        saved_job = Job.objects.get(pk=job.pk)
        # The job state should remain unchanged
        self.assertEqual(saved_job.state, job.state)
        saved_job.dataset.update_from_last_job()  # Sync the associated dataset
        self.assertDatasetState(saved_job.dataset, is_processing=True)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_processing(self, mock_batch_terminate_job):
        # Set up 3 jobs in PROCESSING state
        for _ in range(3):
            JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))

        # Should call terminate_job 3 times for processing, incompleted jobs
        response = Job.terminate_processing()
        mock_batch_terminate_job.assert_called()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)
        self.assertNotEqual(response, [])

        # After termination, the jobs should be saved with TERMINATED state
        for saved_job in Job.objects.all():
            self.assertEqual(saved_job.state, JobStates.TERMINATED)
            self.assertIsInstance(saved_job.terminated_at, datetime)
            saved_job.dataset.update_from_last_job()  # Sync the associated dataset
            self.assertDatasetState(
                saved_job.dataset,
                is_processing=False,
                is_terminated=True,
                terminated_reason=saved_job.terminated_reason,
            )

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_processing_failure(self, mock_batch_terminate_job):
        # Set up mock for 3 unsuccessful terminations
        for _ in range(3):
            JobFactory(state=JobStates.PROCESSING, dataset=DatasetFactory(is_processing=True))
        mock_batch_terminate_job.return_value = []

        # Should call terminate_job 3 times, each time with an exception
        response = Job.terminate_processing()
        mock_batch_terminate_job.assert_called()
        self.assertEqual(mock_batch_terminate_job.call_count, 3)
        self.assertEqual(response, [])

        # After termination, the jobs should remain unchanged
        for saved_job in Job.objects.all():
            self.assertEqual(saved_job.state, JobStates.PROCESSING)
            self.assertIsNone(saved_job.terminated_at)
            saved_job.dataset.update_from_last_job()  # Sync the associated dataset
            self.assertDatasetState(saved_job.dataset, is_processing=True)

    @patch("scpca_portal.batch.terminate_job")
    def test_terminate_processing_no_termination(self, mock_batch_terminate_job):
        # Set up jobs that are already in the final states
        for state in common.FINAL_JOB_STATES:
            JobFactory(state=state, dataset=DatasetFactory(is_processing=False))
        mock_batch_terminate_job.return_value = []

        # Should return an empty list without calling terminate_job
        response = Job.terminate_processing()
        mock_batch_terminate_job.assert_not_called()
        self.assertEqual(response, [])  # No termination with no error

    def test_get_retry_job(self):
        # Set up a non-terminated job
        job = JobFactory(
            state=JobStates.PROCESSING,
            dataset=DatasetFactory(is_processing=True),
        )

        with self.assertRaises(Exception) as e:
            job.get_retry_job()
            self.assertEqual(str(e.exception), "Jobs in final states cannot be retried.")

        # Change the job state to TERMINATED
        job.state = JobStates.TERMINATED

        # Set up mock field values for base terminated jobs
        job.batch_job_name = "BATCH_JOB_NAME"
        job.batch_job_definition = "BATCH_JOB_DEFINITION"
        job.batch_job_queue = "BATCH_JOB_QUEUE"
        job.batch_container_overrides = "BATCH_CONTAINER_OVERRIDES"
        job.attempt = 1

        # After execution, the call should returns a new saved instance for retry
        retry_job = job.get_retry_job()
        # Should correctly copy the exsiting field values
        self.assertEqual(retry_job.batch_job_name, job.batch_job_name)
        self.assertEqual(retry_job.batch_job_definition, job.batch_job_definition)
        self.assertEqual(retry_job.batch_job_queue, job.batch_job_queue)
        self.assertEqual(retry_job.attempt, job.attempt + 1)

    def test_create_retry_jobs(self):
        # Set up mock field values for base terminated jobs
        batch_job_name = "BATCH_JOB_NAME"
        batch_job_definition = "BATCH_JOB_DEFINITION"
        batch_job_queue = "BATCH_JOB_QUEUE"
        batch_container_overrides = "BATCH_CONTAINER_OVERRIDES"
        attempt = 1
        # Set up 3 base terminated jobs for retry
        terminated_jobs = [
            JobFactory(
                state=JobStates.TERMINATED,
                batch_job_name=batch_job_name,
                batch_job_definition=batch_job_definition,
                batch_job_queue=batch_job_queue,
                batch_container_overrides=batch_container_overrides,
                attempt=attempt,
                dataset=DatasetFactory(is_processing=False),
            )
            for _ in range(3)
        ]

        # Before retry, there are 3 jobs in the db
        self.assertEqual(Job.objects.count(), 3)

        # After retry, the call should return a list of jobs for retry
        retry_jobs = Job.create_retry_jobs(terminated_jobs)
        self.assertNotEqual(retry_jobs, [])

        # Should be 6 jobs (base 3  + new 3) in the db
        self.assertEqual(Job.objects.count(), 6)
        # Make sure that the job is saved in the db with correct field values
        saved_retry_jobs = Job.objects.filter(state=JobStates.PENDING)

        for job in saved_retry_jobs:
            self.assertEqual(job.state, JobStates.PENDING)
            # Should correctly copy the base instance's field values
            self.assertEqual(job.batch_job_name, batch_job_name)
            self.assertEqual(job.batch_job_definition, batch_job_definition)
            self.assertEqual(job.batch_job_queue, batch_job_queue)
            self.assertEqual(job.batch_container_overrides, batch_container_overrides)
            self.assertEqual(job.attempt, 2)  # The base's attempt(1) + 1

    @patch(
        "scpca_portal.models.dataset.Dataset.has_lockfile_projects",
        new_callable=PropertyMock,
        return_value=[],
    )
    @patch("scpca_portal.batch.submit_job")
    def test_dynamically_set_dataset_job_pipeline(self, mock_batch_submit_job, _):
        # Set up mock for submit_job
        mock_batch_job_id = "MOCK_JOB_ID"  # The job id returned via AWS Batch response
        mock_batch_submit_job.return_value = mock_batch_job_id

        dataset = DatasetFactory()
        with patch.object(
            Dataset, "estimated_size_in_bytes", new_callable=PropertyMock
        ) as mock_size:
            # job size is below threshold
            mock_size.return_value = Job.MAX_FARGATE_SIZE_IN_BYTES - 1000
            dataset_job = Job.get_dataset_job(dataset)
            dataset_job.submit()
            self.assertEqual(dataset_job.batch_job_queue, settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME)
            self.assertEqual(
                dataset_job.batch_job_definition, settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
            )

            # job size is at threshold
            mock_size.return_value = Job.MAX_FARGATE_SIZE_IN_BYTES
            dataset_job = Job.get_dataset_job(dataset)
            dataset_job.submit()
            self.assertEqual(dataset_job.batch_job_queue, settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME)
            self.assertEqual(
                dataset_job.batch_job_definition, settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
            )

            # job size is above threshold
            mock_size.return_value = Job.MAX_FARGATE_SIZE_IN_BYTES + 1000
            dataset_job = Job.get_dataset_job(dataset)
            dataset_job.submit()
            self.assertEqual(dataset_job.batch_job_queue, settings.AWS_BATCH_EC2_JOB_QUEUE_NAME)
            self.assertEqual(
                dataset_job.batch_job_definition, settings.AWS_BATCH_EC2_JOB_DEFINITION_NAME
            )

    def test_increment_attempt_or_fail(self):
        job = JobFactory(state=JobStates.PENDING, dataset=DatasetFactory(is_processing=False))

        for _ in range(common.MAX_JOB_ATTEMPTS):
            self.assertEqual(job.state, JobStates.PENDING)
            job.increment_attempt_or_fail()

        self.assertEqual(job.state, JobStates.FAILED)
