"""
Coverage for Project/Sample/Library's sync_model and sync_metadata classmethods
(scpca_portal/models/loadable_resource_abc.py), run against the real test S3 bucket instead of
synthetic factory data.

test_project.py/test_sample.py/test_library.py already cover sync_model/sync_metadata's branches
with one hand-built factory instance at a time. This module instead runs the real
sync_original_files -> sync_model -> sync_metadata sequence against the actual test bucket
snapshot (a handful of real projects with real samples/libraries, one of which - SCPCP999993 -
ships already locked), to get coverage against realistic, multi-resource data.

See docs/sync_pipeline_test_plan.md for the full rationale. In short: docs/proposed_test_bucket_
changes.md proposes restructuring the test bucket into a sequence of snapshots so that state
transitions (locking, unlocking, tainting, deletion) can be exercised against real successive
bucket diffs. That hasn't landed yet, so this module simulates the "next" bucket state each
transition needs by mutating OriginalFile rows directly and/or patching get_metadata_dicts_by_id,
while everything else - bucket listing, metadata parsing, resource creation - runs for real.

KNOWN BUG surfaced by this module: Library.sync_model() currently raises KeyError against this
real dataset, because SCPCP999990's spatial library (SCPCL999991) has no "project_id" key in its
real metadata.json, and Library.create_new_objects has no fallback for that (see
TestSyncModelCreatesRealResources.test_library_sync_model_raises_on_real_spatial_metadata for the
pinned repro). Every other Library-focused test in this module routes around that one entry via
_library_metadata_without_known_bad_entry(), noted at each call site; the routing should be
removed once the underlying bug is fixed.
"""

import copy
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import s3
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Library, OriginalFile, Project, Sample
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import OriginalFileFactory

# Real sample/library ids per real project, in the current test bucket snapshot. SCPCP999993 is
# omitted: it ships locked (see test_lockfile.py), so its samples_metadata.csv is excluded from
# the OriginalFile sync entirely (OriginalFile.get_syncable_files drops a locked project's files
# other than its lockfile) and it has no samples/libraries in the DB until it's unlocked.
PROJECT_SAMPLE_IDS = {
    "SCPCP999990": ["SCPCS999990", "SCPCS999991", "SCPCS999994", "SCPCS999997"],
    "SCPCP999991": ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
    "SCPCP999992": ["SCPCS999996", "SCPCS999998"],
}
PROJECT_LIBRARY_IDS = {
    "SCPCP999990": ["SCPCL999990", "SCPCL999991", "SCPCL999994", "SCPCL999997"],
    "SCPCP999991": ["SCPCL999992", "SCPCL999995"],
    "SCPCP999992": ["SCPCL999996", "SCPCL999998"],
}
KNOWN_BAD_LIBRARY_ID = "SCPCL999991"

PROJECT_TEST_DATA = [
    test_data.Project_SCPCP999990,
    test_data.Project_SCPCP999991,
    test_data.Project_SCPCP999992,
]

# sync_metadata only calls update_from_dict - it never rolls values up from a resource's
# samples/libraries. These fields are populated by sync_aggregations instead (out of scope here
# per docs/sync_pipeline_test_plan.md), so they're excluded from the field-value parity checks
# below. Verified empirically: as of this writing every other VALUES key already matches.
PROJECT_AGGREGATE_ONLY_FIELDS = {
    "diagnoses_counts",
    "disease_timings",
    "downloadable_sample_count",
    "has_single_cell_data",
    "modalities",
    "multiplexed_sample_count",
    "organisms",
    "sample_count",
    "seq_units",
    "technologies",
    "unavailable_samples_count",
}
# Every one of these is rolled up from the sample's libraries by new_update_modality_properties/
# new_update_aggregate_properties (models/sample.py) - sync_metadata's update_from_dict never
# touches them, so they sit at their field defaults until sync_aggregations runs.
SAMPLE_AGGREGATE_ONLY_FIELDS = {
    "demux_cell_count_estimate_sum",
    "has_bulk_rna_seq",
    "has_cite_seq_data",
    "has_multiplexed_data",
    "has_single_cell_data",
    "has_spatial_data",
    "includes_anndata",
    "multiplexed_with",
    "sample_cell_count_estimate",
    "seq_units",
    "technologies",
}


def _library_metadata_without_known_bad_entry():
    """
    Library.get_metadata_dicts_by_id(), with the one real entry that has no scpca_project_id
    filtered out. See the module docstring's KNOWN BUG note.
    """
    metadata_by_id = Library.get_metadata_dicts_by_id()
    return {
        library_id: metadata
        for library_id, metadata in metadata_by_id.items()
        if metadata.get("scpca_project_id")
    }


class TestSyncModelCreatesRealResources(TestCase):
    """
    sync_model against the real, current test bucket snapshot, with nothing mocked (aside from
    the Library workaround below): a handful of real projects with real samples/libraries, one of
    which (SCPCP999993) ships already locked.
    """

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    def test_project_sync_model(self):
        output_counts = Project.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 4, "deleted": 0, "locked": 1, "unlocked": 0, "tainted": 0},
        )

        for project_data in PROJECT_TEST_DATA:
            project = Project.objects.get(scpca_id=project_data.SCPCA_ID)
            self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

        # SCPCP999993 ships locked in the real bucket (test_lockfile.py), so it comes out of
        # sync_model LOCKED, without ever passing through NEW.
        locked_project = Project.objects.get(scpca_id="SCPCP999993")
        self.assertEqual(locked_project.loaded_state, LoadableResourceStates.LOCKED)

    def test_sample_sync_model(self):
        Project.sync_model()
        output_counts = Sample.sync_model()

        total_samples = sum(len(ids) for ids in PROJECT_SAMPLE_IDS.values())
        self.assertDictEqual(
            output_counts,
            {"created": total_samples, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        for project_id, sample_ids in PROJECT_SAMPLE_IDS.items():
            samples = Sample.objects.filter(project__scpca_id=project_id)
            self.assertSetEqual(set(samples.values_list("scpca_id", flat=True)), set(sample_ids))
            for sample in samples:
                self.assertEqual(sample.loaded_state, LoadableResourceStates.NEW)

        # locked project's samples aren't synced yet - see PROJECT_SAMPLE_IDS' comment above.
        self.assertFalse(Sample.objects.filter(project__scpca_id="SCPCP999993").exists())

    def test_library_get_metadata_dicts_by_id_has_a_project_id_gap(self):
        """
        Pins the real-data gap behind the known bug below: SCPCL999991's real metadata.json (a
        spatial library) has no "project_id" key, unlike single-cell/bulk libraries' files.
        """
        metadata_by_id = Library.get_metadata_dicts_by_id()

        self.assertIsNone(metadata_by_id[KNOWN_BAD_LIBRARY_ID].get("scpca_project_id"))

    def test_library_sync_model_raises_on_real_spatial_metadata(self):
        """
        KNOWN BUG: Library.create_new_objects looks up each new library's project via the
        "scpca_project_id" key in its own parsed metadata dict - a key spatial library
        metadata.json files don't carry (see the sibling test above), so this raises KeyError
        for any project with a spatial library. The old load_metadata pipeline never hit this:
        it loaded a project's libraries with the project supplied externally, one project at a
        time, rather than reading the project id back out of each library's own metadata.

        This pins the current (broken) behavior so it's visible rather than silently worked
        around. Every other Library test in this module routes around SCPCL999991 via
        _library_metadata_without_known_bad_entry(). Remove this test once fixed.
        """
        Project.sync_model()
        Sample.sync_model()

        with self.assertRaises(KeyError):
            Library.sync_model()

    def test_library_sync_model_creates_real_resources_excluding_known_bad_entry(self):
        Project.sync_model()
        Sample.sync_model()

        metadata_by_id = _library_metadata_without_known_bad_entry()
        with patch.object(Library, "get_metadata_dicts_by_id", return_value=metadata_by_id):
            output_counts = Library.sync_model()

        total_libraries = sum(len(ids) for ids in PROJECT_LIBRARY_IDS.values()) - 1
        self.assertDictEqual(
            output_counts,
            {"created": total_libraries, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        for project_id, library_ids in PROJECT_LIBRARY_IDS.items():
            expected_ids = set(library_ids) - {KNOWN_BAD_LIBRARY_ID}
            libraries = Library.objects.filter(project__scpca_id=project_id)
            self.assertSetEqual(set(libraries.values_list("scpca_id", flat=True)), expected_ids)
            for library in libraries:
                self.assertEqual(library.loaded_state, LoadableResourceStates.NEW)


class TestSyncMetadataMatchesExpectedValues(TestCase):
    """
    Proves sync_metadata (this pipeline) lands the same field values on Project/Sample/Library
    that loader.create_project (the old load_metadata pipeline, exercised in test_loader.py)
    already proves for the same real bucket data - reusing the existing expected_values test data
    rather than duplicating it.
    """

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        Project.sync_model()
        Sample.sync_model()
        library_metadata = _library_metadata_without_known_bad_entry()
        with patch.object(Library, "get_metadata_dicts_by_id", return_value=library_metadata):
            Library.sync_model()

        Project.sync_metadata()
        Sample.sync_metadata()
        with patch.object(Library, "get_metadata_dicts_by_id", return_value=library_metadata):
            Library.sync_metadata()

    def assertFieldsEqual(self, obj, expected_values, *, exclude=frozenset()):
        for field, expected in expected_values.items():
            if field in exclude:
                continue
            actual = getattr(obj, field)
            self.assertEqual(
                actual, expected, f"{obj}.{field}: expected {expected!r}, got {actual!r}"
            )

    def test_project_field_values(self):
        for project_data in PROJECT_TEST_DATA:
            project = Project.objects.get(scpca_id=project_data.SCPCA_ID)
            self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)
            self.assertFieldsEqual(
                project, project_data.VALUES, exclude=PROJECT_AGGREGATE_ONLY_FIELDS
            )

    def test_sample_field_values(self):
        sample_test_data = [
            test_data.Project_SCPCP999990.Sample_SCPCS999990,
            test_data.Project_SCPCP999990.Sample_SCPCS999991,
            test_data.Project_SCPCP999990.Sample_SCPCS999994,
            test_data.Project_SCPCP999990.Sample_SCPCS999997,
            test_data.Project_SCPCP999991.Sample_SCPCS999992,
            test_data.Project_SCPCP999991.Sample_SCPCS999993,
            test_data.Project_SCPCP999991.Sample_SCPCS999995,
            test_data.Project_SCPCP999992.Sample_SCPCS999996,
            test_data.Project_SCPCP999992.Sample_SCPCS999998,
        ]
        for sample_data in sample_test_data:
            sample = Sample.objects.get(scpca_id=sample_data.SCPCA_ID)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.SYNCED)
            self.assertFieldsEqual(sample, sample_data.VALUES, exclude=SAMPLE_AGGREGATE_ONLY_FIELDS)

    def test_library_field_values(self):
        library_test_data = [
            test_data.Project_SCPCP999990.Library_SCPCL999990,
            # SCPCL999991 excluded - known bug, see TestSyncModelCreatesRealResources above
            test_data.Project_SCPCP999990.Library_SCPCL999994,
            test_data.Project_SCPCP999990.Library_SCPCL999997,
            test_data.Project_SCPCP999991.Library_SCPCL999992,
            test_data.Project_SCPCP999991.Library_SCPCL999995,
            test_data.Project_SCPCP999992.Library_SCPCL999996,
            test_data.Project_SCPCP999992.Library_SCPCL999998,
        ]
        for library_data in library_test_data:
            library = Library.objects.get(scpca_id=library_data.SCPCA_ID)
            self.assertEqual(library.loaded_state, LoadableResourceStates.SYNCED)
            self.assertFieldsEqual(library, library_data.VALUES)


class TestSyncModelStateTransitions(TestCase):
    """
    Exercises taint_and_lock_objects' transition branches (locking, unlocking with/without a
    change, deletion, creation) against real project ids from the test bucket, instead of one
    hand-built factory instance per branch.

    Scoped to Project: create_new_objects/remove_deleted_objects/taint_and_lock_objects are
    shared verbatim by Sample and Library via LoadableResourceABC, and each already has its own
    synthetic coverage for the same branches (test_sample.py, test_library.py).

    The real bucket is still a single static snapshot, so the "next" state each scenario needs
    is simulated by mutating OriginalFile rows directly and/or patching
    get_metadata_dicts_by_id, rather than coming from a second real snapshot - see the module
    docstring and docs/sync_pipeline_test_plan.md.
    """

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        Project.sync_metadata()
        cls.real_projects_metadata = Project.get_metadata_dicts_by_id()

    def test_unlocking_a_project_for_the_first_time_becomes_new(self):
        """
        SCPCP999993 ships already locked and has never been synced (loaded_at is None).
        taint_and_lock_objects resets a never-synced resource to NEW when it's unlocked, rather
        than comparing hashes - there's no prior hash to compare against - so this shouldn't
        become SYNCED or TAINTED. Real evidence for RFC open question 2's "nothing to compare
        yet" case (docs/rfc_automated_reload_pipeline.md).
        """
        project = Project.objects.get(scpca_id="SCPCP999993")
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)
        self.assertIsNone(project.loaded_at)

        real_objects = s3.list_bucket_objects(settings.AWS_S3_INPUT_BUCKET_NAME)
        unlocked_objects = [obj for obj in real_objects if not obj["s3_key"].endswith(".lock")]
        with patch("scpca_portal.s3.list_bucket_objects", return_value=unlocked_objects):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.NEW)

    def test_locking_a_previously_synced_project(self):
        project = Project.objects.get(scpca_id="SCPCP999990")
        self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        Project.sync_model()

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)

    def test_unlocking_with_no_change_reverts_to_synced(self):
        project = Project.objects.get(scpca_id="SCPCP999991")
        OriginalFileFactory(project_id="SCPCP999991", is_lockfile=True)
        Project.sync_model()
        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.LOCKED)

        OriginalFile.objects.filter(project_id="SCPCP999991", is_lockfile=True).delete()
        with patch.object(
            Project, "get_metadata_dicts_by_id", return_value=self.real_projects_metadata
        ):
            output_counts = Project.sync_model()

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)
        self.assertEqual(output_counts["unlocked"], 1)
        self.assertEqual(output_counts["tainted"], 0)

    def test_unlocking_with_a_changed_file_hash_reverts_to_tainted(self):
        """Isolates the file-hash half of combined_hash from the metadata half (below)."""
        project = Project.objects.get(scpca_id="SCPCP999991")
        OriginalFileFactory(project_id="SCPCP999991", is_lockfile=True)
        Project.sync_model()

        changed_file = OriginalFile.objects.filter(
            project_id="SCPCP999991", is_lockfile=False
        ).first()
        changed_file.hash = "mutated_hash_value"
        changed_file.save(update_fields=["hash"])

        OriginalFile.objects.filter(project_id="SCPCP999991", is_lockfile=True).delete()
        with patch.object(
            Project, "get_metadata_dicts_by_id", return_value=self.real_projects_metadata
        ):
            output_counts = Project.sync_model()

        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(output_counts["tainted"], 1)

    def test_unlocking_with_changed_metadata_taints_then_resync_lands_new_value(self):
        """Isolates the metadata half of combined_hash, then proves re-sync heals it."""
        project = Project.objects.get(scpca_id="SCPCP999990")
        self.assertEqual(project.title, "Title1")

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        Project.sync_model()

        mutated_metadata = copy.deepcopy(self.real_projects_metadata)
        mutated_metadata["SCPCP999990"]["title"] = "Mutated Title"
        OriginalFile.objects.filter(project_id="SCPCP999990", is_lockfile=True).delete()

        with patch.object(Project, "get_metadata_dicts_by_id", return_value=mutated_metadata):
            output_counts = Project.sync_model()
        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(output_counts["tainted"], 1)
        # sync_model only flips state; field values move on the next sync_metadata call.
        self.assertEqual(project.title, "Title1")

        with patch.object(Project, "get_metadata_dicts_by_id", return_value=mutated_metadata):
            Project.sync_metadata()
        project.refresh_from_db()
        self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)
        self.assertEqual(project.title, "Mutated Title")

    def test_project_deletion_cascades_to_samples_and_libraries(self):
        Sample.sync_model()
        library_metadata = _library_metadata_without_known_bad_entry()
        with patch.object(Library, "get_metadata_dicts_by_id", return_value=library_metadata):
            Library.sync_model()

        self.assertTrue(Sample.objects.filter(project__scpca_id="SCPCP999992").exists())
        self.assertTrue(Library.objects.filter(project__scpca_id="SCPCP999992").exists())

        OriginalFile.objects.filter(project_id="SCPCP999992").delete()
        remaining_metadata = {
            project_id: metadata
            for project_id, metadata in self.real_projects_metadata.items()
            if project_id != "SCPCP999992"
        }
        with patch.object(Project, "get_metadata_dicts_by_id", return_value=remaining_metadata):
            output_counts = Project.sync_model()

        # >0 rather than an exact number: Project's delete() cascades (on_delete=CASCADE) to its
        # samples, libraries, summaries, etc., so the total reflects every row removed with it.
        self.assertGreater(output_counts["deleted"], 0)
        self.assertFalse(Project.objects.filter(scpca_id="SCPCP999992").exists())
        self.assertFalse(Sample.objects.filter(project__scpca_id="SCPCP999992").exists())
        self.assertFalse(Library.objects.filter(project__scpca_id="SCPCP999992").exists())

    def test_new_project_appears_in_metadata(self):
        """
        The one scenario real data can't help with: the current bucket has nothing "not yet
        synced" to point at, so this stays synthetic, same as test_project.py::test_sync_model.
        """
        # make shallow copy of project metadata so other tests don't consume it
        new_projects_metadata = dict(self.real_projects_metadata)
        new_projects_metadata["SCPCP999999"] = {"scpca_project_id": "SCPCP999999"}

        with patch.object(Project, "get_metadata_dicts_by_id", return_value=new_projects_metadata):
            output_counts = Project.sync_model()

        self.assertEqual(output_counts["created"], 1)
        new_project = Project.objects.get(scpca_id="SCPCP999999")
        self.assertEqual(new_project.loaded_state, LoadableResourceStates.NEW)
