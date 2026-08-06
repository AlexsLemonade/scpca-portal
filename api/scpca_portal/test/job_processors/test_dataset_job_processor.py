from datetime import datetime
from unittest.mock import patch

# from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import DatasetStates, FailedJobActions, JobStates
from scpca_portal.exceptions import DatasetMissingLibrariesError, S3TaggingError, S3UploadError
from scpca_portal.job_processors import DatasetJobProcessor
from scpca_portal.test.factories import CCDLDatasetFactory, JobFactory, UserDatasetFactory


class TestDatasetJobProcessor(TestCase):
    def setUp(self):
        self.exception_actions = {
            ("create_new_computed_file", DatasetMissingLibrariesError): FailedJobActions.EMAIL,
            ("upload_new_computed_file", S3UploadError): FailedJobActions.RETRY,
            ("tag_new_computed_file", S3TaggingError): FailedJobActions.SLACK,
        }

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

    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_email_notification_exceptions(self, mock_send_email):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        step = "create_new_computed_file"
        exception = DatasetMissingLibrariesError()

        processor.handle_failure(step, exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        mock_send_email.assert_called_once_with(job)

    @patch("scpca_portal.notifications.send_slack_notification")
    def test_handle_slack_notification_exceptions(self, mock_send_slack):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        step = "tag_new_computed_file"
        exception = S3TaggingError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.handle_failure(step, exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        mock_send_slack.assert_called_once_with(job)

    def test_handle_retryable_exceptions(self):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        step = "upload_new_computed_file"
        exception = S3UploadError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.handle_failure(step, exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        # Should create a new retry job
        self.assertEqual(job.dataset.latest_job.state, JobStates.PENDING)
