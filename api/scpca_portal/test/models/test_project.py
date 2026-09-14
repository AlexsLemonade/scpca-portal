from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, tag
from django.utils.timezone import make_aware

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Project
from scpca_portal.test.factories import LeafProjectFactory, OriginalFileFactory, ProjectFactory


class TestProject(TestCase):

    @tag("lock_projects")
    def test_lock_projects(self):
        projects = [ProjectFactory() for _ in range(3)]
        for project in projects:
            self.assertFalse(project.is_locked)

        project_ids = [p.scpca_id for p in projects]
        Project.lock_projects(project_ids)

        for project in Project.objects.filter(scpca_id__in=project_ids):
            self.assertTrue(project.is_locked)

    def test_sync_metadata(self):
        original_loaded_at_timestamp = make_aware(datetime.now())

        new_project = LeafProjectFactory(loaded_state=LoadableResourceStates.NEW)
        tainted_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.TAINTED, loaded_at=original_loaded_at_timestamp
        )
        # synced project should be left untouched
        synced_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.SYNCED, loaded_at=original_loaded_at_timestamp
        )

        updatable_projects = [new_project, tainted_project]

        metadata_by_id = {
            new_project.scpca_id: {
                "scpca_project_id": new_project.scpca_id,
                "abstract": "New Abstract",
                "human_readable_pi_name": "New Pi",
                "pi_name": "new_pi",
                "title": "New Title",
                "has_bulk_rna_seq": "True",
            },
            tainted_project.scpca_id: {
                "scpca_project_id": tainted_project.scpca_id,
                "abstract": "Tainted Abstract",
                "human_readable_pi_name": "Tainted Pi",
                "pi_name": "tainted_pi",
                "title": "Tainted Title",
                "has_bulk_rna_seq": "False",
            },
        }

        with patch.object(
            Project, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            Project.sync_metadata()

            # verify inputs (only NEW and TAINTED resources are passed through for metadata lookup)
            mock_get_metadata.assert_called_once()
            resources_arg = mock_get_metadata.call_args.kwargs["resources"]
            self.assertListEqual(
                sorted([project.scpca_id for project in resources_arg]),
                sorted([new_project.scpca_id, tainted_project.scpca_id]),
            )

            # verify outputs
            # (each project is updated from its own metadata dict, marked synced, and persisted)
            for project in updatable_projects:
                project.refresh_from_db()

            self.assertEqual(new_project.abstract, "New Abstract")
            self.assertEqual(new_project.human_readable_pi_name, "New Pi")
            self.assertEqual(new_project.pi_name, "new_pi")
            self.assertEqual(new_project.title, "New Title")
            self.assertTrue(new_project.has_bulk_rna_seq)

            self.assertEqual(tainted_project.abstract, "Tainted Abstract")
            self.assertEqual(tainted_project.human_readable_pi_name, "Tainted Pi")
            self.assertEqual(tainted_project.pi_name, "tainted_pi")
            self.assertEqual(tainted_project.title, "Tainted Title")
            self.assertFalse(tainted_project.has_bulk_rna_seq)

            for project in updatable_projects:
                self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)
                self.assertGreater(project.loaded_at, original_loaded_at_timestamp)

            # verify synced project was not touched
            synced_project.refresh_from_db()
            self.assertEqual(synced_project.loaded_at, original_loaded_at_timestamp)

    def test_sync_metadata_no_updatable_resource(self):
        LeafProjectFactory(loaded_state=LoadableResourceStates.SYNCED)

        with patch.object(Project, "get_metadata_dicts_by_id") as mock_get_metadata:
            Project.sync_metadata()

        mock_get_metadata.assert_not_called()

    def test_sync_model(self):
        # DELETED: no longer has any associated original files, and isn't in current metadata
        to_be_deleted_project = LeafProjectFactory()

        # CREATED: only referenced by incoming metadata, doesn't exist in the DB yet
        new_project_id = "SCPCP999901"

        # LOCKED: has a lockfile in the input bucket
        newly_locked_project = LeafProjectFactory(loaded_state=LoadableResourceStates.SYNCED)
        OriginalFileFactory(project_id=newly_locked_project.scpca_id, is_lockfile=True)

        # UNLOCKED & SYNCED: was locked, its lockfile has since been removed,
        # and its metadata is unchanged
        unlocked_synced_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.LOCKED, loaded_at=make_aware(datetime.now())
        )
        unlocked_synced_metadata = {
            "scpca_project_id": unlocked_synced_project.scpca_id,
            "title": "Unchanged Title",
        }
        unlocked_synced_project.combined_hash = unlocked_synced_project.get_current_combined_hash(
            unlocked_synced_metadata
        )
        unlocked_synced_project.save(update_fields=["combined_hash"])

        # UNLOCKED & TAINTED: was locked, its lockfile has since been removed,
        # and its metadata has changed
        unlocked_tainted_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.LOCKED,
            loaded_at=make_aware(datetime.now()),
            combined_hash="outdated_combined_hash",
        )
        unlocked_tainted_metadata = {
            "scpca_project_id": unlocked_tainted_project.scpca_id,
            "title": "New Title",
        }

        metadata_by_id = {
            new_project_id: {"scpca_project_id": new_project_id},
            unlocked_synced_project.scpca_id: unlocked_synced_metadata,
            unlocked_tainted_project.scpca_id: unlocked_tainted_metadata,
        }

        with patch.object(
            Project, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            output_counts = Project.sync_model()

        # verify inputs
        mock_get_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )

        # verify outputs
        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 1, "locked": 1, "unlocked": 1, "tainted": 1},
        )

        self.assertFalse(Project.objects.filter(scpca_id=to_be_deleted_project.scpca_id).exists())
        self.assertTrue(Project.objects.filter(scpca_id=new_project_id).exists())

        newly_locked_project.refresh_from_db()
        self.assertEqual(newly_locked_project.loaded_state, LoadableResourceStates.LOCKED)

        unlocked_synced_project.refresh_from_db()
        self.assertEqual(unlocked_synced_project.loaded_state, LoadableResourceStates.SYNCED)

        unlocked_tainted_project.refresh_from_db()
        self.assertEqual(unlocked_tainted_project.loaded_state, LoadableResourceStates.TAINTED)

    def test_sync_model_no_changes(self):
        with patch.object(Project, "get_metadata_dicts_by_id", return_value={}):
            output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

    def test_sync_aggregations(self):
        # bulk is turned off for now, the bulk path will be tested when actual test data is used
        stale_project = ProjectFactory(
            has_bulk_rna_seq=False, aggregation_hash="stale_hash", sample_count=0
        )
        for sample in stale_project.samples.all():
            sample.metadata_hash = "sample_hash"
            sample.save(update_fields=["metadata_hash"])
        for library in stale_project.libraries.all():
            library.metadata_hash = "library_hash"
            library.save(update_fields=["metadata_hash"])

        # placeholder sample_count proves this project's aggregations are left untouched
        up_to_date_project = ProjectFactory(has_bulk_rna_seq=False, sample_count=999)
        for sample in up_to_date_project.samples.all():
            sample.metadata_hash = "sample_hash_2"
            sample.save(update_fields=["metadata_hash"])
        for library in up_to_date_project.libraries.all():
            library.metadata_hash = "library_hash_2"
            library.save(update_fields=["metadata_hash"])
        up_to_date_project.aggregation_hash = up_to_date_project.current_aggregation_hash
        up_to_date_project.save(update_fields=["aggregation_hash"])

        resources = Project.objects.filter(id__in=[stale_project.id, up_to_date_project.id])
        Project.sync_aggregations(resources)

        stale_project.refresh_from_db()
        up_to_date_project.refresh_from_db()

        # stale project's aggregations were recomputed and its hash brought up to date
        self.assertEqual(stale_project.aggregation_hash, stale_project.current_aggregation_hash)
        self.assertEqual(stale_project.sample_count, 1)

        # up-to-date project was left untouched
        self.assertEqual(up_to_date_project.sample_count, 999)

    def test_sync_aggregations_no_changes(self):
        project = LeafProjectFactory(sample_count=999)
        project.aggregation_hash = project.current_aggregation_hash
        project.save(update_fields=["aggregation_hash"])

        Project.sync_aggregations(Project.objects.filter(id=project.id))

        project.refresh_from_db()
        self.assertEqual(project.sample_count, 999)
