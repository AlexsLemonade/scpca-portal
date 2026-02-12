from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import JobFactory, UserDatasetFactory


class TestSyncBatchJobs(TestCase):
    def setUp(self):
        self.sync_batch_jobs = partial(call_command, "sync_batch_jobs")

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

    @patch("scpca_portal.batch.get_jobs")
    def test_sync_batch_jobs(self, mock_batch_get_jobs):
        # Set up mock jobs
        self.jobs = [
            JobFactory(
                state=JobStates.PROCESSING,
                batch_job_id=batch_job_id,
                dataset=UserDatasetFactory(
                    is_processing=True, processing_at=make_aware(datetime.now())
                ),
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
        mock_response[6]["statusReason"] = "Job FAILED"
        mock_response[7]["status"] = "FAILED"  # MOCK_JOB_ID_7
        mock_response[7]["isTerminated"] = True
        mock_response[7]["statusReason"] = "Job TERMINATED"
        mock_batch_get_jobs.return_value = mock_response

        self.sync_batch_jobs()

        mock_batch_get_jobs.assert_called_once()

        self.assertEqual(Job.objects.exclude(state=JobStates.PROCESSING).count(), 3)

        # PROCESSING job should remain unchanged
        processing_job = Job.objects.filter(state=JobStates.PROCESSING).first()
        self.assertDatasetState(processing_job.dataset, is_processing=True)

        # SUCCEEDED job state and dataset should be updated
        succeeded_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_5").first()
        self.assertEqual(succeeded_job.state, JobStates.SUCCEEDED)
        self.assertDatasetState(succeeded_job.dataset, is_succeeded=True)

        # FAILED job state and dataset should be updated with failed reason
        failed_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_6").first()
        self.assertEqual(failed_job.state, JobStates.FAILED)
        self.assertDatasetState(failed_job.dataset, is_failed=True, failed_reason="Job FAILED")

        # TERMINATED job state and dataset should be updated
        terminated_job = Job.objects.filter(batch_job_id="MOCK_JOB_ID_7").first()
        self.assertDatasetState(
            terminated_job.dataset, is_terminated=True, terminated_reason="Job TERMINATED"
        )
