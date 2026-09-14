from functools import partial
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal.models import Library, Project, Sample


class TestSyncModels(TestCase):
    """
    sync_model itself is tested on Project/Sample/Library's own test classes, so it's
    mocked out here. These tests only cover this command's own inputs (the arguments it
    passes through to sync_model).
    """

    def setUp(self):
        self.sync_models = partial(call_command, "sync_models")

        self.project_output_counts = {
            "created": 1,
            "deleted": 2,
            "locked": 3,
            "unlocked": 4,
            "tainted": 5,
        }
        self.sample_output_counts = {
            "created": 6,
            "deleted": 7,
            "locked": 8,
            "unlocked": 9,
            "tainted": 10,
        }
        self.library_output_counts = {
            "created": 11,
            "deleted": 12,
            "locked": 13,
            "unlocked": 14,
            "tainted": 15,
        }

        project_sync_model_patch = patch.object(
            Project, "sync_model", return_value=self.project_output_counts
        )
        sample_sync_model_patch = patch.object(
            Sample, "sync_model", return_value=self.sample_output_counts
        )
        library_sync_model_patch = patch.object(
            Library, "sync_model", return_value=self.library_output_counts
        )

        self.mock_project_sync_model = project_sync_model_patch.start()
        self.mock_sample_sync_model = sample_sync_model_patch.start()
        self.mock_library_sync_model = library_sync_model_patch.start()

        self.patches = [
            project_sync_model_patch,
            sample_sync_model_patch,
            library_sync_model_patch,
        ]

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_inputs_default_args(self):
        self.sync_models()

        self.mock_project_sync_model.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )
        self.mock_sample_sync_model.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )
        self.mock_library_sync_model.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )

    def test_inputs_passed_through_args(self):
        custom_bucket = "custom-bucket"
        self.sync_models(bucket=custom_bucket, skip_existing_file_download=True)

        self.mock_project_sync_model.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
        self.mock_sample_sync_model.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
        self.mock_library_sync_model.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
