from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import lockfile


class TestLockfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    def test_get_is_locked_project(self):
        non_locked_project_id = "SCPCP999990"
        locked_project_id = "SCPCP999993"

        self.assertFalse(lockfile.get_is_locked_project(non_locked_project_id))
        self.assertTrue(lockfile.get_is_locked_project(locked_project_id))

    def test_get_locked_project_ids(self):
        expected_project_ids = [
            "SCPCP999993",
        ]
        self.assertListEqual(lockfile.get_locked_project_ids(), expected_project_ids)
