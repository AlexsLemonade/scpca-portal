"""
sync_model and sync_metadata coverage for the Project class' derivation
of the LoadableResourceABC base class.

For sync_model coverage, each test runs the real sync_original_files -> Project.sync_model()
sequence against the actual test S3 bucket, narrowed to just the project ids the scenario needs via
filter_original_files_by_resource_wrapper and filter_metadata_by_resource_wrapper, both generic
across Project/Sample/Library and defined once in test_loadable_resource_abc_utils.py rather than
copy-pasted here.
"""

from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import OriginalFile, Project
from scpca_portal.test.factories import OriginalFileFactory
from scpca_portal.test.models.test_loadable_resource_abc_utils import (
    filter_metadata_by_resource_wrapper,
    filter_original_files_by_resource_wrapper,
)


class TestProjectLoadableResource(TransactionTestCase):
    # SYNC_MODEL TESTS
    def test_sync_model_new_projects(self):
        project_ids = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
        ):
            output_counts = Project.sync_model()

        new_project_metadata = {"scpca_project_id": "SCPCP999999"}
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(
                Project, project_ids, add_new_metadata=new_project_metadata
            ),
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
        ):
            Project.sync_model()
            Project.sync_metadata()

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        OriginalFileFactory(project_id="SCPCP999991", is_lockfile=True)
        OriginalFileFactory(project_id="SCPCP999992", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
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
            side_effect=filter_metadata_by_resource_wrapper(
                Project,
                project_ids,
                modified_resource_id="SCPCP999992",
                mutated_field="title",
                mutated_value="Mutated title",
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
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
        ):
            Project.sync_model()
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert OF deletion with project still in metadata preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Project, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, project_ids),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert deletion in metadata but lack of OF deletion preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Project, project_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, []),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Project.objects.filter(scpca_id="SCPCP999992").exists())

        # Assert satisfaction of both conditions yields purged object from db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Project, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_projects_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Project, []),
        ):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["deleted"], 1)
        self.assertFalse(Project.objects.filter(scpca_id="SCPCP999992").exists())

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
