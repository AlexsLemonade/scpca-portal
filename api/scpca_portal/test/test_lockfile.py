from unittest.mock import patch

from django.test import TestCase

from scpca_portal import lockfile


# TODO: update tests when lockfile added to test input bucket
class TestLockfile(TestCase):
    def test_get_lockfile_project_ids(self):
        with patch("scpca_portal.s3.check_file_empty", return_value=True):
            self.assertListEqual(lockfile.get_lockfile_project_ids(), [])

        with patch("scpca_portal.s3.check_file_empty", return_value=False), patch(
            "scpca_portal.s3.download_files"
        ):
            # assert that pre-existing local lockfile is ignored during processing
            lockfile.LOCKFILE_PATH.touch()
            lockfile.LOCKFILE_PATH.write_text("SCPCP999990\nSCPCP999991")
            self.assertListEqual(lockfile.get_lockfile_project_ids(), [])
            self.assertFalse(lockfile.LOCKFILE_PATH.exists())

            # assert that lockfile ids are processed correctly
            with patch("pathlib.Path.unlink"):
                lockfile.LOCKFILE_PATH.touch()
                lockfile.LOCKFILE_PATH.write_text("SCPCP999990\nSCPCP999991")
                self.assertListEqual(
                    lockfile.get_lockfile_project_ids(), ["SCPCP999990", "SCPCP999991"]
                )
