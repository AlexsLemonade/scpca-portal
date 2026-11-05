from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal import common
from scpca_portal.enums import DatasetStates, JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import CCDLDatasetFactory, JobFactory


class TestSubmitPending(TestCase):
    def setUp(self):
        self.submit_pending = partial(call_command, "submit_pending")

    def assertDatasetState(self, dataset, job_state):
        """
        Helper for asserting the dataset state.
        """
        if job_state in [JobStates.PENDING, JobStates.PROCESSING]:
            self.assertEqual(dataset.state, DatasetStates.PROCESSING)

        if job_state == JobStates.SUCCEEDED:
            self.assertEqual(dataset.state, DatasetStates.SUCCEEDED)

        if job_state in [JobStates.FAILED, JobStates.TERMINATED]:
            self.assertEqual(dataset.state, DatasetStates.FAILED)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending(self, mock_batch_submit_job):
        # Set up 3 PENDING jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.PENDING,
                dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING),
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
            self.assertDatasetState(saved_job.dataset, JobStates.PROCESSING)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_pending_not_called(self, mock_batch_submit_job):
        # Set up 4 jobs that are either in processing or in the final states
        for state in common.SUBMITTED_JOB_STATES:
            JobFactory(state=state, dataset=CCDLDatasetFactory())

        # Should not call submit_job
        self.submit_pending()
        mock_batch_submit_job.assert_not_called()
