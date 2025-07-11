from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal import lockfile
from scpca_portal.models import OriginalFile

# from django.core.management import call_command


# TODO: update tests when lockfile added to test input bucket
class TestLockfile(TestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    # TODO: test should be uncommented when lockfile is added
    # def test_get_lockfile_project_ids(self):
    def get_lockfile_project_ids(self):
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
        with patch("pathlib.Path.unlink"):
            self.assertListEqual(
                lockfile.get_lockfile_project_ids(), ["SCPCP999990", "SCPCP999991"]
            )
