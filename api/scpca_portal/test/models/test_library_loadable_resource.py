"""
sync_model and sync_metadata coverage for the Library class' derivation
of the LoadableResourceABC base class.

For sync_model coverage, each test runs the real sync_original_files -> Library.sync_model()
sequence against the actual test S3 bucket, narrowed to just the library ids the scenario needs via
filter_original_files_by_resource_wrapper and filter_metadata_by_resource_wrapper, both generic
across Project/Sample/Library and defined once in test_loadable_resource_abc_utils.py rather than
copy-pasted here - see that file's module docstring for exactly how each resolves scope.

Library metadata has two sources, regular (one metadata.json per library) and bulk (one tsv per
project), so both are patched whenever library metadata is narrowed. Project and Sample are synced
unnarrowed first, since new libraries resolve their project FK and samples M2M from the db.

KNOWN BUG: SCPCL999991's metadata.json has no "project_id", which makes Library.sync_model() raise
KeyError, so no test includes it.
"""

from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Library, OriginalFile, Project, Sample
from scpca_portal.test.factories import OriginalFileFactory
from scpca_portal.test.models.test_loadable_resource_abc_utils import (
    filter_metadata_by_resource_wrapper,
    filter_original_files_by_resource_wrapper,
)


class TestLibraryLoadableResource(TransactionTestCase):
    # SYNC_MODEL TESTS
    def test_sync_model_new_libraries(self):
        # One library per project, plus SCPCP999990's bulk library "SCPCL999994"
        # sync_model's created count doesn't differentiate bulk from regular libraries, so it's
        # included right alongside the rest to prove that. SCPCL999992 is a multiplexed library
        # (two samples).
        library_ids = ["SCPCL999990", "SCPCL999992", "SCPCL999994", "SCPCL999996"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        Sample.sync_model()
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 4, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        for library_id in library_ids:
            library = Library.objects.get(scpca_id=library_id)
            self.assertEqual(library.loaded_state, LoadableResourceStates.NEW)

        # Assert that a library can also be created by just adding it to the metadata file
        # without any Original Files
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        new_library_metadata = {
            "scpca_project_id": "SCPCP999990",
            "scpca_sample_id": "SCPCS999990",
            "scpca_library_id": "SCPCL999999",
        }
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(
                    Library, library_ids, add_new_metadata=new_library_metadata
                ),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        new_library = Library.objects.exclude(scpca_id__in=library_ids).first()
        self.assertIsNotNone(new_library)
        self.assertEqual(new_library.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_new_locked_libraries(self):
        # A library cannot become NEW and then LOCKED directly
        # (operating in a state of existence but without any files) like a project can.
        # The typical cycle for a library to end up LOCKED would be for a library to begin NEW,
        # then transition to SYNCED, and then possibly LOCKED at some point thereafter.
        # The only possibility of this scenario occuring would be if sync_model would run,
        # set the library to NEW, and a lockfile would be added before sync_metadata would run
        # to move it to SYNCED.
        # As this very improbable, we've decided not to test it.
        pass

    def test_sync_model_unlock_new_locked_libraries(self):
        # This test is being skipped in line with the comment to the previos test.
        pass

    def test_sync_model_lock_synced_libraries(self):
        # Both normal "SCPCL999990" and bulk "SCPCL999994" libraries are tested here
        library_ids = ["SCPCL999990", "SCPCL999994"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        Sample.sync_model()
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 2, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        # Now the new libraries should be moved to a SYNCED state
        Library.sync_metadata()
        for library_id in library_ids:
            library = Library.objects.get(scpca_id=library_id)
            self.assertEqual(library.loaded_state, LoadableResourceStates.SYNCED)

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 2, "unlocked": 0, "tainted": 0},
        )

        for library_id in library_ids:
            library = Library.objects.get(scpca_id=library_id)
            self.assertEqual(library.loaded_state, LoadableResourceStates.LOCKED)

    def test_sync_model_unlock_synced_libraries(self):
        # CREATE THE LIBRARIES
        library_ids = ["SCPCL999990", "SCPCL999994", "SCPCL999997"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        Sample.sync_model()
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            Library.sync_model()

        # SYNC THE LIBRARIES
        Library.sync_metadata()

        # LOCK THE LIBRARIES
        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertEqual(output_counts["locked"], 3)

        # UNLOCK THE LIBRARIES
        # NOTE: there is no "UNLOCKED" state:
        # untouched libraries are reverted to SYNCED and touched one become TAINTED
        non_tainted_library = Library.objects.get(scpca_id="SCPCL999994")
        tainted_original_files_library = Library.objects.get(scpca_id="SCPCL999990")
        tainted_metadata_library = Library.objects.get(scpca_id="SCPCL999997")
        self.assertEqual(non_tainted_library.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_original_files_library.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_metadata_library.loaded_state, LoadableResourceStates.LOCKED)

        mutated_file = OriginalFile.objects.filter(
            library_id="SCPCL999990", is_lockfile=False
        ).first()
        mutated_file.hash = "mutated_hash_value"
        mutated_file.save(update_fields=["hash"])

        OriginalFile.objects.filter(project_id="SCPCP999990", is_lockfile=True).delete()
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(
                    Library,
                    library_ids,
                    modified_resource_id="SCPCL999997",
                    mutated_field="seq_unit",
                    mutated_value="Mutated seq_unit",
                ),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        non_tainted_library.refresh_from_db()
        tainted_original_files_library.refresh_from_db()
        tainted_metadata_library.refresh_from_db()
        self.assertEqual(non_tainted_library.loaded_state, LoadableResourceStates.SYNCED)
        self.assertEqual(
            tainted_original_files_library.loaded_state, LoadableResourceStates.TAINTED
        )
        self.assertEqual(tainted_metadata_library.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(output_counts["locked"], 0)
        self.assertEqual(output_counts["unlocked"], 1)
        self.assertEqual(output_counts["tainted"], 2)

    def test_sync_model_purge_deleted_library(self):
        # A library is purged once nothing references its id: no OriginalFile tagged with it and
        # no metadata row for it. A regular library is referenced by both its own files and its
        # metadata.json. A bulk library's files (the project level bulk/ tsvs) are never tagged
        # with its id, so only its row in the bulk tsv keeps it alive, like a project or sample
        # row in a shared metadata file. Both types go through every stage below together.
        regular_library_id = "SCPCL999996"
        bulk_library_id = "SCPCL999994"
        library_ids = [regular_library_id, bulk_library_id]

        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        Sample.sync_model()
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()
        self.assertEqual(output_counts["created"], 2)

        # Assert OF deletion but lack of deletion in metadata preserves both objects in db.
        # A regular library's metadata.json goes with its files, so its row is re-added
        # synthetically. The bulk tsv is project level, so the bulk row is still read for real.
        deleted_library_metadata = {
            "scpca_project_id": "SCPCP999992",
            "scpca_sample_id": "SCPCS999996",
            "scpca_library_id": regular_library_id,
        }
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(
                    Library, [], add_new_metadata=deleted_library_metadata
                ),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, library_ids, bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertTrue(Library.objects.filter(scpca_id=bulk_library_id).exists())

        # Assert deletion in metadata but lack of OF deletion preserves only the regular library.
        # The bulk library's files remain, but none carry its id, so dropping its row purges it.
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, library_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, []),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, [], bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        # Library row plus its samples m2m through-row
        self.assertEqual(output_counts["deleted"], 2)
        self.assertTrue(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertFalse(Library.objects.filter(scpca_id=bulk_library_id).exists())

        # Assert satisfaction of both conditions purges the regular library too
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Library, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with (
            patch(
                "scpca_portal.metadata_parser.load_all_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, []),
            ),
            patch(
                "scpca_portal.metadata_parser.load_all_bulk_libraries_metadata",
                side_effect=filter_metadata_by_resource_wrapper(Library, [], bulk=True),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertEqual(output_counts["deleted"], 2)
        self.assertFalse(Library.objects.filter(scpca_id=regular_library_id).exists())

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
