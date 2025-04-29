from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestSyncBatchJobs(TestCase):
    def setUp(self):
        self.sync_batch_jobs = partial(call_command, "sync_batch_jobs")

    def assertDatasetState(
        self,
        dataset,
        is_processing=False,
        is_processed=False,
        is_errored=False,
        error_message=None,
        is_terminated=False,
    ):
        """
        Helper for asserting the dataset state.
        """
        self.assertEqual(dataset.is_processing, is_processing)

        self.assertEqual(dataset.is_processed, is_processed)
        if is_processed:
            self.assertIsInstance(dataset.processed_at, datetime)

        self.assertEqual(dataset.is_errored, is_errored)
        if is_errored:
            self.assertIsInstance(dataset.errored_at, datetime)
        self.assertEqual(dataset.error_message, error_message)

        self.assertEqual(dataset.is_terminated, is_terminated)
        if is_terminated:
            self.assertIsInstance(dataset.terminated_at, datetime)

    @patch("scpca_portal.batch.get_jobs")
    def test_sync_batch_jobs(self, mock_batch_get_jobs):
        # Set up mock jobs
        self.jobs = [
            JobFactory(
                state=JobStates.SUBMITTED,
                batch_job_id=batch_job_id,
                dataset=DatasetFactory(is_processing=True),
            )
            for batch_job_id in [
                "MOCK_JOB_ID_0",
                "MOCK_JOB_ID_1",
                "MOCK_JOB_ID_2",
                "MOCK_JOB_ID_3",
                "MOCK_JOB_ID_4",
                "MOCK_JOB_ID_5",
                "MOCK_JOB_ID_6",
                "MOCK_JOB_ID_7",
            ]
        ]
        # Set up mock for get_jobs
        mock_response = [{"jobId": job.batch_job_id} for job in self.jobs]
        # All AWS Batch job statuses (7) + FAILED & terminated job (1)
        mock_response[0]["status"] = "SUBMITTED"
        mock_response[1]["status"] = "PENDING"
        mock_response[2]["status"] = "RUNNABLE"
        mock_response[3]["status"] = "STARTING"
        mock_response[4]["status"] = "RUNNING"
        mock_response[5]["status"] = "SUCCEEDED"  # MOCK_JOB_ID_5
        mock_response[6]["status"] = "FAILED"  # MOCK_JOB_ID_6
        mock_response[7]["status"] = "FAILED"  # MOCK_JOB_ID_7
        mock_response[7]["isTerminated"] = True
        mock_response = [{**job, "statusReason": f"Job {job['status']}"} for job in mock_response]
        mock_batch_get_jobs.return_value = mock_response

        self.sync_batch_jobs()

        mock_batch_get_jobs.assert_called_once()

        self.assertEqual(Job.objects.exclude(state=JobStates.SUBMITTED).count(), 3)

        # SUBMITTED job should remain unchanged
        submitted_job = Job.objects.filter(state=JobStates.SUBMITTED).first()
        self.assertDatasetState(
            submitted_job.dataset,
            is_processing=True,
            is_processed=False,
            is_errored=False,
            error_message=None,
            is_terminated=False,
        )

        # SUCCEEDED job state and dataset should be updated
        succeeded_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_5").first()
        self.assertEqual(succeeded_job.state, JobStates.SUCCEEDED)
        self.assertDatasetState(
            succeeded_job.dataset,
            is_processing=False,
            is_processed=True,
            is_errored=False,
            error_message=None,
            is_terminated=False,
        )

        # FAILED job state and dataset should be updated with failed reason
        failed_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_6").first()
        self.assertEqual(failed_job.state, JobStates.FAILED)
        self.assertDatasetState(
            failed_job.dataset,
            is_processing=False,
            is_processed=False,
            is_errored=True,
            error_message="Job FAILED",
            is_terminated=False,
        )

        # TERMINATED job state and dataset should be updated
        terminated_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_7").first()
        self.assertDatasetState(
            terminated_job.dataset,
            is_processing=False,
            is_processed=False,
            is_errored=False,
            error_message=None,
            is_terminated=True,
        )
