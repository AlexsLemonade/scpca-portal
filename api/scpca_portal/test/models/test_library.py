from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal import common
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Library
from scpca_portal.test.factories import (
    LeafProjectFactory,
    LibraryFactory,
    OriginalFileFactory,
    SampleFactory,
)


class TestLibrary(TestCase):
    def test_sync_metadata(self):
        original_loaded_at_timestamp = make_aware(datetime.now())

        new_library = LibraryFactory(loaded_state=LoadableResourceStates.NEW)
        tainted_library = LibraryFactory(
            loaded_state=LoadableResourceStates.TAINTED, loaded_at=original_loaded_at_timestamp
        )
        # synced library should be left untouched
        synced_library = LibraryFactory(
            loaded_state=LoadableResourceStates.SYNCED, loaded_at=original_loaded_at_timestamp
        )

        updatable_libraries = [new_library, tainted_library]

        metadata_by_id = {
            new_library.scpca_id: {
                "scpca_library_id": new_library.scpca_id,
                "is_multiplexed": True,
                "modality": "SINGLE_CELL",
                "workflow_version": "1.2.3",
            },
            tainted_library.scpca_id: {
                "scpca_library_id": tainted_library.scpca_id,
                "is_multiplexed": False,
                "modality": "SPATIAL",
                "workflow_version": "4.5.6",
            },
        }

        with patch.object(
            Library, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            Library.sync_metadata()

            # verify inputs (only NEW and TAINTED resources are passed through for metadata lookup)
            mock_get_metadata.assert_called_once()
            resources_arg = mock_get_metadata.call_args.kwargs["resources"]
            self.assertListEqual(
                sorted([library.scpca_id for library in resources_arg]),
                sorted([new_library.scpca_id, tainted_library.scpca_id]),
            )

            # verify outputs
            # (each library is updated from its own metadata dict, marked synced, and persisted)
            for library in updatable_libraries:
                library.refresh_from_db()

            self.assertTrue(new_library.is_multiplexed)
            self.assertEqual(new_library.workflow_version, "1.2.3")

            self.assertFalse(tainted_library.is_multiplexed)
            self.assertEqual(tainted_library.workflow_version, "4.5.6")

            for library in updatable_libraries:
                self.assertEqual(library.loaded_state, LoadableResourceStates.SYNCED)
                self.assertGreater(library.loaded_at, original_loaded_at_timestamp)

            # verify synced library was not touched
            synced_library.refresh_from_db()
            self.assertEqual(synced_library.loaded_at, original_loaded_at_timestamp)

    def test_sync_metadata_no_updatable_resource(self):
        LibraryFactory(loaded_state=LoadableResourceStates.SYNCED)

        with patch.object(Library, "get_metadata_dicts_by_id") as mock_get_metadata:
            Library.sync_metadata()

        mock_get_metadata.assert_not_called()

    def test_sync_model(self):
        project = LeafProjectFactory()

        # DELETED: no longer referenced by any original file, and isn't in current metadata
        to_be_deleted_library = LibraryFactory(project=project)

        # CREATED: only referenced by incoming metadata, doesn't exist in the DB yet.
        # Multiplexed libraries list their associated sample ids as a single delimited string
        # (e.g. "SCPCS999992,SCPCS999993") rather than a single sample id.
        new_library_id = "SCPCL999901"
        multiplexed_sample_1 = SampleFactory(project=project)
        multiplexed_sample_2 = SampleFactory(project=project)
        new_library_sample_id = common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER.join(
            [multiplexed_sample_1.scpca_id, multiplexed_sample_2.scpca_id]
        )

        # LOCKED: its project has a lockfile in the input bucket
        locked_project = LeafProjectFactory()
        locked_project_sample = SampleFactory(project=locked_project)
        newly_locked_library = LibraryFactory(
            project=locked_project, loaded_state=LoadableResourceStates.SYNCED
        )
        newly_locked_library.samples.add(locked_project_sample)
        OriginalFileFactory(project_id=locked_project.scpca_id, is_lockfile=True)

        # UNLOCKED & SYNCED: was locked, its project's lockfile has since been removed,
        # and its metadata is unchanged
        unlocked_synced_library = LibraryFactory(
            project=project,
            loaded_state=LoadableResourceStates.LOCKED,
            loaded_at=make_aware(datetime.now()),
        )
        unlocked_synced_metadata = {
            "scpca_library_id": unlocked_synced_library.scpca_id,
            "workflow_version": "1.2.3",
        }
        unlocked_synced_library.combined_hash = unlocked_synced_library.get_current_combined_hash(
            unlocked_synced_metadata
        )
        unlocked_synced_library.save(update_fields=["combined_hash"])

        # UNLOCKED & TAINTED: was locked, its project's lockfile has since been removed,
        # and its metadata has changed
        unlocked_tainted_library = LibraryFactory(
            project=project,
            loaded_state=LoadableResourceStates.LOCKED,
            loaded_at=make_aware(datetime.now()),
            combined_hash="outdated_combined_hash",
        )
        unlocked_tainted_metadata = {
            "scpca_library_id": unlocked_tainted_library.scpca_id,
            "workflow_version": "4.5.6",
        }

        metadata_by_id = {
            new_library_id: {
                "scpca_project_id": project.scpca_id,
                "scpca_sample_id": new_library_sample_id,
                "scpca_library_id": new_library_id,
            },
            # present so it survives remove_deleted_objects; locking doesn't need its metadata
            newly_locked_library.scpca_id: {
                "scpca_project_id": locked_project.scpca_id,
                "scpca_sample_id": locked_project_sample.scpca_id,
                "scpca_library_id": newly_locked_library.scpca_id,
            },
            unlocked_synced_library.scpca_id: unlocked_synced_metadata,
            unlocked_tainted_library.scpca_id: unlocked_tainted_metadata,
        }

        with patch.object(
            Library, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            output_counts = Library.sync_model()

        # verify inputs
        mock_get_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )

        # verify outputs
        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 1, "locked": 1, "unlocked": 1, "tainted": 1},
        )

        self.assertFalse(Library.objects.filter(scpca_id=to_be_deleted_library.scpca_id).exists())
        new_library = Library.objects.filter(scpca_id=new_library_id, project=project).first()
        self.assertIsNotNone(new_library)
        self.assertEqual(
            set(new_library.samples.values_list("scpca_id", flat=True)),
            {multiplexed_sample_1.scpca_id, multiplexed_sample_2.scpca_id},
        )

        newly_locked_library.refresh_from_db()
        self.assertEqual(newly_locked_library.loaded_state, LoadableResourceStates.LOCKED)

        unlocked_synced_library.refresh_from_db()
        self.assertEqual(unlocked_synced_library.loaded_state, LoadableResourceStates.SYNCED)

        unlocked_tainted_library.refresh_from_db()
        self.assertEqual(unlocked_tainted_library.loaded_state, LoadableResourceStates.TAINTED)

    def test_sync_model_no_changes(self):
        with patch.object(Library, "get_metadata_dicts_by_id", return_value={}):
            output_counts = Library.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
