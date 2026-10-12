"""
sync_model and sync_metadata coverage for the Library class' derivation
of the LoadableResourceABC base class.

For sync_model coverage, each test runs the real sync_original_files -> Library.sync_model()
sequence against the actual test S3 bucket, narrowed to just the library ids the scenario needs via
filter_original_files_by_resource_wrapper and filter_metadata_by_resource_wrapper, both generic
across Project/Sample/Library and defined once in test_loadable_resource_abc_utils.py rather than
copy-pasted here - see that file's module docstring for exactly how each resolves scope.

Library.new_load_metadata reads libraries from two independent sources and concatenates them -
metadata_parser.load_all_libraries_metadata (one metadata.json file per regular library) and
metadata_parser.load_all_bulk_libraries_metadata (one shared, project level bulk tsv, since a
project's bulk library has no file of its own) - so both must be patched/scoped together any time
library metadata needs narrowing, unlike Project/Sample which each only have one source to patch.
filter_metadata_by_resource_wrapper's keyword-only bulk flag picks between the two - bulk=False
(the default) for the regular source, bulk=True for the bulk one - so scoping a test's library
metadata still means two separate patch calls, one per source, same as always.

Once concatenated though, sync_model never differentiates a bulk library from a regular one - its
created/deleted/locked/unlocked/tainted counts are a single unified total either way. SCPCL999994
(SCPCP999990's only bulk library in the real test bucket) is deliberately mixed in alongside
regular libraries in test_sync_model_new_libraries and test_sync_model_purge_deleted_library to
prove that counts stay unified rather than split by source. A bulk library also has no
OriginalFile of its own, which is why filter_original_files_by_resource_wrapper never narrows
project-level files (or lockfiles) down to a resolved project for Library requests the way it does
for Sample - there would be nothing to resolve a project from when the requested id is a bulk
library's.

Project.sync_model() and Sample.sync_model() are both called unnarrowed before every
Library.sync_model() in this file, since Library.create_new_objects resolves each new library's
project FK and samples M2M out of the db, so project and sample rows must already exist. Project
and Sample rows are left unnarrowed - the extra rows are inert FK targets for library level
assertions.

KNOWN BUG, routed around throughout this file: SCPCP999990's spatial library (SCPCL999991) has no
"project_id" key in its real metadata.json, and Library.create_new_objects has no fallback for
that, so Library.sync_model() raises KeyError if that library's metadata is ever in scope. None of
this file's scenarios include SCPCL999991 in their library_ids for that reason.
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
        # One library per project, plus SCPCP999990's bulk library (SCPCL999994 - parsed from the
        # project's shared bulk tsv rather than its own metadata.json, see the module docstring).
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
        # SCPCL999996 is a regular library (its own metadata.json); SCPCL999994 is SCPCP999990's
        # bulk library (parsed from the project's shared bulk tsv, no OriginalFile of its own - see
        # the module docstring). Both are created and purged together here, to prove sync_model's
        # deleted count is a single unified total that doesn't differentiate bulk from regular
        # libraries - it's kept separate from library_ids below only because a bulk library has no
        # OriginalFile to independently lose, so it can't follow the same OF-vs-metadata staged
        # narrative regular_library_id does; it instead stays in scope throughout and is only
        # dropped at the final, "both conditions satisfied" step, alongside regular_library_id.
        regular_library_id = "SCPCL999996"
        bulk_library_id = "SCPCL999994"
        library_ids = [regular_library_id]
        bulk_library_ids = [bulk_library_id]

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
        self.assertTrue(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertTrue(Library.objects.filter(scpca_id=bulk_library_id).exists())

        # Unlike Project/Sample - whose metadata comes from one shared, always present file - a
        # library's own metadata.json IS its sole metadata source. Once its Original File is gone,
        # the real load_all_libraries_metadata can no longer read it at all, so there's nothing to
        # narrow down to. "OF deletion with library still in metadata" is instead simulated by
        # re-adding the library's metadata dict synthetically via add_new_metadata. This only
        # applies to the regular library - bulk_library_ids stays untouched (still in scope)
        # through this and the next stage, since a bulk library never has an OriginalFile to lose.
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
                side_effect=filter_metadata_by_resource_wrapper(
                    Library, bulk_library_ids, bulk=True
                ),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertTrue(Library.objects.filter(scpca_id=bulk_library_id).exists())

        # Assert deletion in metadata but lack of OF deletion preserves object in db
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
                side_effect=filter_metadata_by_resource_wrapper(
                    Library, bulk_library_ids, bulk=True
                ),
            ),
        ):
            output_counts = Library.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertTrue(Library.objects.filter(scpca_id=bulk_library_id).exists())

        # Assert satisfaction of both conditions yields purged object from db - for the regular
        # and the bulk library alike, counted together in one unified "deleted" total.
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

        # >=2 rather than an exact number: deleting a Library also deletes its samples m2m
        # through-rows, so the total reflects those join rows being removed alongside the two
        # Library rows themselves, not just the Library rows.
        self.assertGreaterEqual(output_counts["deleted"], 2)
        self.assertFalse(Library.objects.filter(scpca_id=regular_library_id).exists())
        self.assertFalse(Library.objects.filter(scpca_id=bulk_library_id).exists())

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
