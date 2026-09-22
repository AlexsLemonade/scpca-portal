from datetime import datetime
from unittest.mock import patch

# from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import DatasetStates, JobStates
from scpca_portal.exceptions import (
    DatasetLockedProjectError,
    DatasetMissingLibrariesError,
    S3TaggingError,
    S3UploadError,
)
from scpca_portal.job_processors import DatasetJobProcessor
from scpca_portal.models import Job
from scpca_portal.test.factories import CCDLDatasetFactory, JobFactory, UserDatasetFactory


class TestDatasetJobProcessor(TestCase):
    def test_on_run_done_expires_at_for_user_dataset(self):
        succeeded_at = make_aware(datetime.now())

        job = JobFactory(
            state=JobStates.SUCCEEDED,
            succeeded_at=succeeded_at,
            dataset=UserDatasetFactory(state=DatasetStates.SUCCEEDED),
        )
        processor = DatasetJobProcessor(job)
        processor.on_run_done()

        self.assertIsInstance(job.dataset.expires_at, datetime)

    def test_on_run_done_no_expires_at_for_ccdl_dataset(self):
        succeeded_at = make_aware(datetime.now())

        job = JobFactory(
            state=JobStates.SUCCEEDED,
            succeeded_at=succeeded_at,
            dataset=CCDLDatasetFactory(state=DatasetStates.SUCCEEDED),
        )
        processor = DatasetJobProcessor(job)
        processor.on_run_done()

        expected_value = None
        self.assertIsNone(job.dataset.expires_at, expected_value)

    def test_handle_dataset_locked_project_error(self):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = DatasetLockedProjectError()

        processor.handle_locked_project(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, Job.RETRY_EXIT_CODE)

        # Should create a new retry job
        if processor.job.is_last_batch_attempt:
            self.assertEqual(job.dataset.latest_job.state, JobStates.PENDING)

    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_missing_libraries_error(self, mock_send_email):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        exception = DatasetMissingLibrariesError()

        processor.handle_missing_libraries(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, Job.HALT_EXIT_CODE)

        # Should send the error email notification
        mock_send_email.assert_called_once_with(job)

    def test_handle_s3_upload_error(self):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = S3UploadError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.handle_upload_failure(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, Job.RETRY_EXIT_CODE)

        # Should create a new retry job
        if processor.job.is_last_batch_attempt:
            self.assertEqual(job.dataset.latest_job.state, JobStates.PENDING)

    @patch("scpca_portal.notifications.send_slack_notification")
    def test_handle_s3_tagging_error(self, mock_mock_send_slack):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = S3TaggingError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.handle_tag_failure(exception)

        self.assertEqual(job.state, JobStates.PROCESSING)  # Should remain PROCESSING
        self.assertEqual(processor.exit_code, Job.HALT_EXIT_CODE)

        # Should send the slack notification for manual tagging
        mock_mock_send_slack.assert_called_once_with(job)

    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_uncaught_error(self, mock_send_email):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        exception = Exception("Uncaught error")

        processor.on_uncaught_exception("MOCK_STEP", exception)

        self.assertEqual(job.state, JobStates.PROCESSING)  # Should remain PROCESSING
        self.assertEqual(processor.exit_code, Job.RETRY_EXIT_CODE)

        # Should send the error email notification
        if processor.job.is_last_batch_attempt:
            mock_send_email.assert_called_once_with(job)
