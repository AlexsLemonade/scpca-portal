from typing import List
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal.models import OriginalFile

# Capture the real (bound) classmethod before any patching occurs.
# Must run at import time — capturing while a patch is active would
# grab the mock instead and cause infinite recursion.
current_original_files = OriginalFile.get_syncable_files


def filter_by_projects_wrapper(project_ids: List[str]):
    """
    Build a side_effect for patching OriginalFile.get_syncable_files.
    Returns a replacement that delegates to the real implementation,
    then narrows the resulting original files and lockfiles to the given project IDs.
    """

    def filter_by_projects(*arg, **kwargs):
        # Run the real classmethod with the original args (*args, **kwargs) to ensure whatever
        # arguments the command originally passed (bucket_objects, bucket, sync_timestamp) are used.
        original_files, lockfiles = current_original_files(*arg, **kwargs)

        filtered_original_files = [of for of in original_files if of.project_id in project_ids]
        filtered_lockfiles = [lf for lf in lockfiles if lf.project_id in project_ids]

        return filtered_original_files, filtered_lockfiles

    return filter_by_projects


class TestProjectLoadableResource(TransactionTestCase):
    def setUp(self):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    # SYNC_MODEL TESTS
    def test_sync_model(self):
        project_ids = ["SCPCP999990", "SCPCP999991"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_by_projects_wrapper(project_ids),
        ):
            call_command("sync_models")

    def test_sync_metadata(self):
        pass
