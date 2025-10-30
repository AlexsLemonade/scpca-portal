from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import lockfile
from scpca_portal.models import OriginalFile


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

    def test_get_lockfile_project_ids(self):
        lockfile_original_file = OriginalFile.objects.filter(
            s3_key=lockfile.LOCKFILE_S3_KEY, s3_bucket=settings.AWS_S3_INPUT_BUCKET_NAME
        ).first()

        # assert that lockfile is empty
        self.assertListEqual(lockfile.get_lockfile_project_ids(), [])

        # create local lockfile
        lockfile_original_file.local_file_path.touch()
        lockfile_original_file.local_file_path.write_text("SCPCP999990\nSCPCP999991")
        lockfile_original_file.size_in_bytes = lockfile_original_file.local_file_path.stat().st_size
        lockfile_original_file.save()

        # assert that created lockfile becomes unlinked, and empty one is downloaded
        self.assertListEqual(lockfile.get_lockfile_project_ids(), [])
        self.assertFalse(lockfile_original_file.local_file_path.exists())

        # re-create local lockfile
        lockfile_original_file.local_file_path.touch()
        lockfile_original_file.local_file_path.write_text("SCPCP999990\nSCPCP999991")
        lockfile_original_file.size_in_bytes = lockfile_original_file.local_file_path.stat().st_size
        lockfile_original_file.save()

        # mock unlinking, and assert that lockfile ids are processed correctly
        with patch("pathlib.Path.unlink"), patch("scpca_portal.s3.download_files"):
            self.assertListEqual(
                lockfile.get_lockfile_project_ids(), ["SCPCP999990", "SCPCP999991"]
            )
        lockfile_original_file.local_file_path.unlink()

    def test_get_lockfile_project_ids_with_file_check(self):
        with patch("scpca_portal.s3.check_file_empty") as mock_check_file_empty:
            mock_check_file_empty.return_value = True

            project_ids = lockfile.get_lockfile_project_ids_with_file_check()
            mock_check_file_empty.assert_called_once()
            self.assertListEqual(project_ids, [])

            with patch("scpca_portal.lockfile.get_lockfile_project_ids") as mock_wrapped_method:
                mock_check_file_empty.return_value = False

                lockfile.get_lockfile_project_ids_with_file_check()
                mock_wrapped_method.assert_called_once()
