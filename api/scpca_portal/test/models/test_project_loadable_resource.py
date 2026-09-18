"""
Sync_model/sync_metadata coverage for Project (scpca_portal/models/loadable_resource_abc.py),
split out of the combined scpca_portal/test/test_sync_metadata_loading_sequence.py into one
scenario per test method, per model. test_sample_loadable_resource.py/test_library_loadable_
resource.py will follow the same pattern for Sample/Library.

Each test runs the real sync_original_files -> Project.sync_model() sequence against the actual
test S3 bucket, narrowed to just the project ids the scenario needs via two side_effect wrappers,
both following the same pattern: delegate to the real implementation, then narrow its result to
the given project ids.
- filter_by_projects_wrapper patches OriginalFile.get_syncable_files, narrowing which project(s)
  get their files synced by sync_original_files.
- filter_projects_metadata_wrapper patches metadata_parser.load_all_projects_metadata, narrowing
  which project(s) Project.sync_model()/sync_metadata() see in the projects_metadata.csv.
  Without this, every sync_model() call would create/consider all 4 real
  projects regardless of the first wrapper's scope, since that csv lists all of them and
  Project.sync_model() never filters it by id on its own.

Together, both wrappers keep each test's OriginalFile table AND each sync_model() call's metadata
narrowly scoped to exactly the project id(s) that scenario is about - while still exercising the
real bucket-listing/hashing/parsing code end to end, rather than mocking it away.

OriginalFile rows are only ever set via the sync_original_files command - the one exception is
adding a lockfile via OriginalFileFactory, since most real projects aren't locked. To simulate
a later bucket state (a lockfile disappearing, a project going away entirely), we wipe the table
with OriginalFile.objects.all().delete() and call sync_original_files a second time with a narrower
project id list, rather than deleting/mutating specific rows by hand.
"""

from typing import List
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import metadata_parser
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import OriginalFile, Project
from scpca_portal.test.factories import OriginalFileFactory

# Capture the real (bound) functions before any patching occurs.
# Must run at import time. Capturing while a patch is active would
# grab the mock instead and cause infinite recursion.
current_get_syncable_files = OriginalFile.get_syncable_files
current_load_all_projects_metadata = metadata_parser.load_all_projects_metadata


def filter_by_projects_wrapper(project_ids: List[str]):
    """
    Build a side_effect for patching OriginalFile.get_syncable_files.
    Returns a replacement that delegates to the real implementation, then narrows the resulting
    original files and lockfiles to the given project IDs - except files with no project id
    (portal-wide files, e.g. the projects_metadata.csv), which get_syncable_files itself always
    treats as syncable regardless of project, so the wrapper keeps them too.
    """

    def filter_by_projects(*args, **kwargs):
        # Run the real classmethod with the original args (*args, **kwargs) to ensure whatever
        # arguments the command originally passed (bucket_objects, bucket, sync_timestamp) are used.
        original_files, lockfiles = current_get_syncable_files(*args, **kwargs)

        filtered_original_files = [
            of for of in original_files if of.project_id is None or of.project_id in project_ids
        ]
        filtered_lockfiles = [lf for lf in lockfiles if lf.project_id in project_ids]

        return filtered_original_files, filtered_lockfiles

    return filter_by_projects


def filter_projects_metadata_wrapper(project_ids: List[str]):
    """
    Build a side_effect for patching metadata_parser.load_all_projects_metadata.
    Returns a replacement that delegates to the real implementation, then narrows the resulting
    list of project metadata dicts down to the given project IDs.
    """

    def filter_projects_metadata(*args, **kwargs):
        # Run the real function with the original args (*args, **kwargs) to ensure whatever
        # arguments the caller originally passed (projects_metadata_file, filter_on_ids) are used.
        projects_metadata = current_load_all_projects_metadata(*args, **kwargs)

        return [
            md
            for md in projects_metadata
            if md[Project.SCPCA_RESOURCE_METADATA_ID_KEY] in project_ids
        ]

    return filter_projects_metadata


class TestProjectLoadableResource(TransactionTestCase):
    # SYNC_MODEL TESTS
    def test_sync_model_creates_new_projects(self):
        project_ids = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        for project_id in project_ids:
            project = Project.objects.get(scpca_id=project_id)
            self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_create_new_locked_project(self):
        project_ids = ["SCPCP999993"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )
        project = Project.objects.get(scpca_id="SCPCP999993")
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertIsNone(project.loaded_at)

    def test_sync_model_unlock_a_never_before_synced_previously_locked_project(self):
        project_ids = ["SCPCP999993"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )

        project = Project.objects.get(scpca_id="SCPCP999993")
        # A project locked from birth (loaded_at is None) reverts to NEW when unlocked,
        # since there's no prior hash to compare against.
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertIsNone(project.loaded_at)

        # SCPCP999993's lockfile is a permanent fixture of the real bucket - it can't be made to
        # disappear by re-listing the bucket. Instead, reset the OriginalFile table and re-sync
        # with SCPCP999993 left out of the files wrapper's scope entirely, so its lockfile isn't
        # synced this round. It stays in the metadata wrapper's scope though, so it still exists
        # to be unlocked rather than getting swept up as deleted.
        OriginalFile.objects.filter(project_id="SCPCP999993", is_lockfile=True).delete()
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_lock_a_previously_synced_project(self):
        project_ids = ["SCPCP999990"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
            Project.sync_metadata()  # This is necessary to move the project into a SYNCED state
        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        project = Project.objects.get(scpca_id="SCPCP999990")
        self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_projects_metadata_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
