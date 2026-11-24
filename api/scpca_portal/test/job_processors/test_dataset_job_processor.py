import os
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

    @patch.dict(os.environ, {"HALT_EXIT_CODE": "3"})
    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_email_notification_exceptions(self, mock_send_email):
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        exception = DatasetMissingLibrariesError()

        processor.handle_missing_libraries(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, int(os.environ["HALT_EXIT_CODE"]))

        # Should send the error email notification
        mock_send_email.assert_called_once_with(job)

    @patch.dict(
        os.environ,
        {"AWS_BATCH_JOB_ATTEMPT": "1", "MAX_RETRY_ATTEMPTS": "3", "RETRY_EXIT_CODE": "1"},
    )
    def test_handle_retryable_exceptions_first_attempt_failure(self):
        retry_exit_code = int(os.environ["RETRY_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = DatasetLockedProjectError()

        processor.set_exit_code(retry_exit_code)
        processor.handle_locked_project(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, retry_exit_code)
        # Should not create a new retry job
        self.assertEqual(job.dataset.latest_job.state, JobStates.FAILED)

    @patch.dict(
        os.environ,
        {"AWS_BATCH_JOB_ATTEMPT": "3", "MAX_RETRY_ATTEMPTS": "3", "RETRY_EXIT_CODE": "1"},
    )
    def test_handle_retryable_exceptions_last_attempt_failure(self):
        retry_exit_code = int(os.environ["RETRY_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = S3UploadError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.set_exit_code(retry_exit_code)
        processor.handle_upload_failure(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, retry_exit_code)
        # Should create a new retry job
        if processor.job.is_last_batch_attempt:
            self.assertEqual(job.dataset.latest_job.state, JobStates.PENDING)

    @patch.dict(os.environ, {"HALT_EXIT_CODE": "3"})
    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_missing_libraries_error(self, mock_send_email):
        halt_exit_code = int(os.environ["HALT_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        exception = DatasetMissingLibrariesError()

        processor.set_exit_code(halt_exit_code)
        processor.handle_missing_libraries(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, halt_exit_code)
        # Should send the error email notification without retry attempts
        mock_send_email.assert_called_once_with(job)

    @patch.dict(
        os.environ,
        {"AWS_BATCH_JOB_ATTEMPT": "3", "MAX_RETRY_ATTEMPTS": "3", "RETRY_EXIT_CODE": "1"},
    )
    def test_handle_s3_upload_error_last_attempt_failure(self):
        retry_exit_code = int(os.environ["RETRY_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = S3UploadError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.set_exit_code(retry_exit_code)
        processor.handle_upload_failure(exception)

        self.assertEqual(job.state, JobStates.FAILED)
        self.assertEqual(job.failed_reason, f"{exception}")
        self.assertEqual(processor.exit_code, retry_exit_code)
        # Should create a new retry job
        if processor.job.is_last_batch_attempt:
            self.assertEqual(job.dataset.latest_job.state, JobStates.PENDING)

    @patch.dict(os.environ, {"HALT_EXIT_CODE": "3"})
    @patch("scpca_portal.notifications.send_slack_notification")
    def test_handle_s3_tagging_error(self, mock_mock_send_slack):
        halt_exit_code = int(os.environ["HALT_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(state=DatasetStates.PROCESSING)
        )

        processor = DatasetJobProcessor(job)
        exception = S3TaggingError("MOCK_KEY", "MOCK_BUCKET_NAME")

        processor.set_exit_code(halt_exit_code)
        should_continue_to_next_step = processor.handle_tag_failure(exception)

        self.assertTrue(should_continue_to_next_step)
        self.assertEqual(processor.exit_code, halt_exit_code)
        self.assertEqual(job.state, JobStates.PROCESSING)  # Should remain PROCESSING

        # Should send the slack notification for manual handling
        mock_mock_send_slack.assert_called_once_with(job)

    @patch.dict(
        os.environ,
        {"AWS_BATCH_JOB_ATTEMPT": "3", "MAX_RETRY_ATTEMPTS": "3", "RETRY_EXIT_CODE": "1"},
    )
    @patch("scpca_portal.notifications.send_dataset_job_error_email")
    def test_handle_uncaught_error_last_attempt_failure(self, mock_send_email):
        retry_exit_code = int(os.environ["RETRY_EXIT_CODE"])
        job = JobFactory(
            state=JobStates.PROCESSING, dataset=CCDLDatasetFactory(email="user@example.com")
        )

        processor = DatasetJobProcessor(job)
        exception = Exception("Uncaught error")

        processor.set_exit_code(retry_exit_code)
        processor.on_uncaught_exception("MOCK_STEP", exception)

        self.assertEqual(job.state, JobStates.PROCESSING)  # Should remain PROCESSING
        self.assertEqual(processor.exit_code, retry_exit_code)

        # Should send the error email notification
        if processor.job.is_last_batch_attempt:
            mock_send_email.assert_called_once_with(job)
