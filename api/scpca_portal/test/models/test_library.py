from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Library
from scpca_portal.test.factories import LibraryFactory


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
