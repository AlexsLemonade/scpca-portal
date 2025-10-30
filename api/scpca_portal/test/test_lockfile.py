from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import lockfile


class TestLockfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    @patch("scpca_portal.s3.check_file_exists")
    def test_get_is_locked_project(self, mock_check_files_exist):
        project_id = "SCPCP999990"

        mock_check_files_exist.return_value = True
        self.assertTrue(lockfile.get_is_locked_project(project_id))

        mock_check_files_exist.return_value = False
        self.assertFalse(lockfile.get_is_locked_project(project_id))

    @patch("scpca_portal.s3.list_files_by_suffix")
    def test_get_locked_project_ids(self, mock_list_files_by_suffix):
        project_lockfile_paths = [
            Path("SCPCP999990.lock"),
            Path("SCPCP999991.lock"),
            Path("SCPCP999992.lock"),
        ]
        mock_list_files_by_suffix.return_value = project_lockfile_paths

        expected_project_ids = [
            "SCPCP999990",
            "SCPCP999991",
            "SCPCP999992",
        ]
        self.assertListEqual(lockfile.get_locked_project_ids(), expected_project_ids)
