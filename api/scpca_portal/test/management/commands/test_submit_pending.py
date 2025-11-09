from datetime import datetime
from functools import partial
from unittest.mock import PropertyMock, patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal import common
from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestSubmitBatchJobs(TestCase):
    def setUp(self):
        self.submit_pending = partial(call_command, "submit_pending")

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

    @patch(
        "scpca_portal.models.dataset.Dataset.has_lockfile_projects",
        new_callable=PropertyMock,
        return_value=[],
    )
    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending(self, mock_batch_submit_job, _):
        # Set up 3 PENDING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PENDING,
                dataset=DatasetFactory(is_processing=False),
            )
        mock_batch_submit_job.return_value = "MOCK_JOB_ID"

        # Should call submit_job 3 times
        self.submit_pending()
        self.assertEqual(mock_batch_submit_job.call_count, 3)

        # PENDING jobs should be updated to PROCESSING and datasets marked as processing
        for saved_job in Job.objects.all():
            self.assertEqual(saved_job.state, JobStates.PROCESSING)
            self.assertIsNotNone(saved_job.batch_job_id)
            self.assertIsInstance(saved_job.processing_at, datetime)
            self.assertDatasetState(saved_job.dataset, is_processing=True)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending_not_called(self, mock_batch_submit_job):
        # Set up 4 jobs that are either in processing or in the final states
        for state in common.SUBMITTED_JOB_STATES:
            JobFactory(state=state, dataset=DatasetFactory(is_processing=False))

        # Should not call submit_job
        self.submit_pending()
        mock_batch_submit_job.assert_not_called()
