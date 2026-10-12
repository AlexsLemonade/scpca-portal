"""
sync_model and sync_metadata coverage for the Project class' derivation
of the LoadableResourceABC base class.

For sync_model coverage, each test runs the real sync_original_files -> Project.sync_model()
sequence against the actual test S3 bucket, narrowed to just the project ids the scenario needs
via two side_effect wrappers, filter_original_files_by_projects and filter_metadata_by_projects.
Both follow the same pattern of delegating to the real implementation,
then narrow its result to the given project ids.
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
# grab the mocked function instead, causing infinite recursion.
non_patched_get_syncable_files = OriginalFile.get_syncable_files
non_patched_load_all_projects_metadata = metadata_parser.load_all_projects_metadata


def filter_original_files_by_projects_wrapper(project_ids: List[str]):
    """
    Build a side_effect for patching OriginalFile.get_syncable_files.
    Returns a replacement that delegates to the real implementation, then narrows the resulting
    original files and lockfiles to the given project IDs - except files with no project id
    (portal-wide files, e.g. the projects_metadata.csv), which get_syncable_files itself always
    treats as syncable regardless of project, so the wrapper keeps them too.
    """

    def filter_original_files_by_projects(*args, **kwargs):
        # Run the real classmethod with the original args (*args, **kwargs) to ensure whatever
        # arguments the command originally passed (bucket_objects, bucket, sync_timestamp) are used.
        original_files, lockfiles = non_patched_get_syncable_files(*args, **kwargs)

        filtered_original_files = [
            of for of in original_files if of.project_id is None or of.project_id in project_ids
        ]
        filtered_lockfiles = [lf for lf in lockfiles if lf.project_id in project_ids]

        return filtered_original_files, filtered_lockfiles

    return filter_original_files_by_projects


def filter_metadata_by_projects_wrapper(
    project_ids: List[str], *, add_new_project: bool = False, modified_project_id: str | None = None
):
    """
    Build a side_effect for patching metadata_parser.load_all_projects_metadata.
    Returns a replacement that delegates to the real implementation, then narrows the resulting
    list of project metadata dicts down to the given project IDs.
    """

    def filter_metadata_by_projects(*args, **kwargs):
        # Run the real function with the original args (*args, **kwargs) to ensure whatever
        # arguments the caller originally passed (projects_metadata_file, filter_on_ids) are used.
        projects_metadata = non_patched_load_all_projects_metadata(*args, **kwargs)
        filtered_metadata = [
            md
            for md in projects_metadata
            if md[Project.SCPCA_RESOURCE_METADATA_ID_KEY] in project_ids
        ]

        if add_new_project:
            filtered_metadata.append({"scpca_project_id": "SCPCP999999"})

        if modified_project_id:
            modified_project_metadata = next(
                (md for md in filtered_metadata if md["scpca_project_id"] == modified_project_id),
                None,
            )
            if modified_project_metadata:
                modified_project_metadata["title"] = "Mutated title"

        return filtered_metadata

    return filter_metadata_by_projects


class TestProjectLoadableResource(TransactionTestCase):
    # SYNC_MODEL TESTS
    def test_sync_model_new_projects(self):
        project_ids = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        for project_id in project_ids:
            project = Project.objects.get(scpca_id=project_id)
            self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

        # Assert that a project can also be created by just adding it to the metadata file
        # without any Original Files
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids, add_new_project=True),
        ):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        new_project = Project.objects.exclude(scpca_id__in=project_ids).first()
        self.assertIsNotNone(new_project)
        self.assertEqual(new_project.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_new_locked_project(self):
        project_ids = ["SCPCP999993"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )
        project = Project.objects.get(scpca_id="SCPCP999993")
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertIsNone(project.loaded_at)

    def test_sync_model_unlock_new_locked_project(self):
        project_ids = ["SCPCP999993"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
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
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_lock_synced_project(self):
        project_ids = ["SCPCP999990"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
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
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)

    def test_sync_model_unlock_synced_projects(self):
        project_ids = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            Project.sync_model()
            Project.sync_metadata()

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        OriginalFileFactory(project_id="SCPCP999991", is_lockfile=True)
        OriginalFileFactory(project_id="SCPCP999992", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["locked"], 3)
        non_tainted_project = Project.objects.get(scpca_id="SCPCP999990")
        tainted_original_files_project = Project.objects.get(scpca_id="SCPCP999991")
        tainted_metadata_project = Project.objects.get(scpca_id="SCPCP999992")
        self.assertEqual(non_tainted_project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_original_files_project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_metadata_project.loaded_state, LoadableResourceStates.LOCKED)

        mutated_file = OriginalFile.objects.filter(
            project_id="SCPCP999991", is_lockfile=False
        ).first()
        mutated_file.hash = "mutated_hash_value"
        mutated_file.save(update_fields=["hash"])

        OriginalFile.objects.filter(project_id="SCPCP999990", is_lockfile=True).delete()
        OriginalFile.objects.filter(project_id="SCPCP999991", is_lockfile=True).delete()
        OriginalFile.objects.filter(project_id="SCPCP999992", is_lockfile=True).delete()
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(
                project_ids, modified_project_id="SCPCP999992"
            ),
        ):
            output_counts = Project.sync_model()

        non_tainted_project.refresh_from_db()
        tainted_original_files_project.refresh_from_db()
        tainted_metadata_project.refresh_from_db()
        self.assertEqual(non_tainted_project.loaded_state, LoadableResourceStates.SYNCED)
        self.assertEqual(
            tainted_original_files_project.loaded_state, LoadableResourceStates.TAINTED
        )
        self.assertEqual(tainted_metadata_project.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(output_counts["locked"], 0)
        self.assertEqual(output_counts["unlocked"], 1)
        self.assertEqual(output_counts["tainted"], 2)

    def test_sync_model_purge_deleted_project(self):
        project_ids = ["SCPCP999992"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            Project.sync_model()
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert OF deletion with project still in metadata preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper([]),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper(project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert deletion in metadata but lack of OF deletion preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper(project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper([]),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert satisfaction of both conditions yields purged object from db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_projects_wrapper([]),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_projects_wrapper([]),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 1)
        self.assertFalse(Project.objects.filter(scpca_id="SCPCP999992").exists())

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
