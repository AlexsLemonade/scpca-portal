from datetime import datetime
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums import JobStates
from scpca_portal.models import Job
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestSubmitCreatedBatchJobs(TestCase):
    def setUp(self):
        self.submit_created_batch_jobs = partial(call_command, "submit_created_batch_jobs")

    def assertDatasetState(
        self, dataset, is_processing=False, is_errored=False, errored_at=None, error_message=None
    ):
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
    def test_submit_created_batch_jobs(self, mock_batch_submit_job):
        # Set up 3 CREATED jobs
        for _ in range(3):
            JobFactory(
                state=JobStates.CREATED,
                dataset=DatasetFactory(is_processing=False),
            )

        # Should call submit_job 3 times
        self.submit_created_batch_jobs()
        self.assertEqual(mock_batch_submit_job.call_count, 3)

        # CREATED jobs should be updated to SUBMITTED and datasets marked as processing
        for saved_job in Job.objects.all():
            self.assertEqual(saved_job.state, JobStates.SUBMITTED)
            self.assertIsNotNone(saved_job.batch_job_id)
            self.assertIsInstance(saved_job.submitted_at, datetime)
            self.assertDatasetState(saved_job.dataset, is_processing=True)

    @patch("scpca_portal.batch.submit_job")
    def test_submit_created_batch_jobs_not_called(self, mock_batch_submit_job):
        # Set up 3 already submitted jobs
        for state in [
            JobStates.SUBMITTED.value,
            JobStates.COMPLETED.value,
            JobStates.TERMINATED.value,
        ]:
            JobFactory(state=state, dataset=DatasetFactory(is_processing=False))

        # Should not call submit_job
        self.submit_created_batch_jobs()
        mock_batch_submit_job.assert_not_called()
