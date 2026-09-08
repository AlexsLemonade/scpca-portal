from functools import partial
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal.models import Library, Project, Sample


class TestSyncMetadata(TestCase):
    """
    sync_metadata itself is tested on Project/Sample/Library's own test classes, so it's
    mocked out here. These tests only cover this command's own inputs (the arguments it
    passes through to sync_metadata).
    """

    def setUp(self):
        self.sync_metadata = partial(call_command, "sync_metadata")

        project_sync_metadata_patch = patch.object(Project, "sync_metadata", return_value=1)
        sample_sync_metadata_patch = patch.object(Sample, "sync_metadata", return_value=2)
        library_sync_metadata_patch = patch.object(Library, "sync_metadata", return_value=3)

        self.mock_project_sync_metadata = project_sync_metadata_patch.start()
        self.mock_sample_sync_metadata = sample_sync_metadata_patch.start()
        self.mock_library_sync_metadata = library_sync_metadata_patch.start()

        self.patches = [
            project_sync_metadata_patch,
            sample_sync_metadata_patch,
            library_sync_metadata_patch,
        ]

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_inputs_default_args(self):
        self.sync_metadata()

        self.mock_project_sync_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )
        self.mock_sample_sync_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )
        self.mock_library_sync_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )

    def test_inputs_passed_through_args(self):
        custom_bucket = "custom-bucket"
        self.sync_metadata(bucket=custom_bucket, skip_existing_file_download=True)

        self.mock_project_sync_metadata.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
        self.mock_sample_sync_metadata.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
        self.mock_library_sync_metadata.assert_called_once_with(
            bucket=custom_bucket, skip_existing_file_download=True
        )
