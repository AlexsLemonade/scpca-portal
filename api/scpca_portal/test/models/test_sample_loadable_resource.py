"""
sync_model and sync_metadata coverage for the Sample class' derivation
of the LoadableResourceABC base class.

For sync_model coverage, each test runs the real sync_original_files -> Sample.sync_model()
sequence against the actual test S3 bucket, narrowed to just the sample ids the scenario needs via
filter_original_files_by_resource_wrapper and filter_metadata_by_resource_wrapper, both generic
across Project/Sample/Library and defined once in test_loadable_resource_abc_utils.py rather than
copy-pasted here.

Project is synced unnarrowed first, since new samples resolve their project FK from the db.
"""

from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import OriginalFile, Project, Sample
from scpca_portal.test.factories import OriginalFileFactory
from scpca_portal.test.models.test_loadable_resource_abc_utils import (
    filter_metadata_by_resource_wrapper,
    filter_original_files_by_resource_wrapper,
)


class TestSampleLoadableResource(TransactionTestCase):
    # SYNC_MODEL TESTS
    def test_sync_model_new_samples(self):
        sample_ids = ["SCPCS999990", "SCPCS999995", "SCPCS999996"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        for sample_id in sample_ids:
            sample = Sample.objects.get(scpca_id=sample_id)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.NEW)

        # Assert that a sample can also be created by just adding it to the metadata file
        # without any Original Files
        new_sample_metadata = {"scpca_sample_id": "SCPCS999999", "scpca_project_id": "SCPCP999990"}
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(
                Sample, sample_ids, add_new_metadata=new_sample_metadata
            ),
        ):
            output_counts = Sample.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )
        new_sample = Sample.objects.exclude(scpca_id__in=sample_ids).first()
        self.assertIsNotNone(new_sample)
        self.assertEqual(new_sample.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_new_locked_samples(self):
        # A new project that is locked will not contain any sample files, data or metadata.
        # As such, no new samples should be created.
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        self.assertFalse(
            OriginalFile.objects.filter(project_id="SCPCP999993", is_lockfile=False).exists()
        )

        # Samples locked from birth come from a lockfile being added before their first sync,
        # which sync_model creates and then immediately locks in the same pass.
        sample_ids = ["SCPCS999990", "SCPCS999991", "SCPCS999997"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 3, "unlocked": 0, "tainted": 0},
        )
        for sample_id in sample_ids:
            sample = Sample.objects.get(scpca_id=sample_id)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.LOCKED)
            self.assertIsNone(sample.loaded_at)

    def test_sync_model_unlock_new_locked_samples(self):
        sample_ids = ["SCPCS999990", "SCPCS999991", "SCPCS999997"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 3, "unlocked": 0, "tainted": 0},
        )

        # Samples locked from birth (loaded_at is None) revert to NEW when unlocked,
        # since there's no prior hash to compare against.
        OriginalFile.objects.filter(project_id="SCPCP999990", is_lockfile=True).delete()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        for sample_id in sample_ids:
            sample = Sample.objects.get(scpca_id=sample_id)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.NEW)

    def test_sync_model_lock_synced_samples(self):
        sample_ids = ["SCPCS999990", "SCPCS999991", "SCPCS999997"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()
            Sample.sync_metadata()  # This is necessary to move the samples into a SYNCED state
        self.assertDictEqual(
            output_counts,
            {"created": 3, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

        for sample_id in sample_ids:
            sample = Sample.objects.get(scpca_id=sample_id)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.SYNCED)

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()
        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 3, "unlocked": 0, "tainted": 0},
        )

        for sample_id in sample_ids:
            sample = Sample.objects.get(scpca_id=sample_id)
            self.assertEqual(sample.loaded_state, LoadableResourceStates.LOCKED)

    def test_sync_model_unlock_synced_samples(self):
        # NOTE: all three samples belong to SCPCP999990, since a lockfile is project level -
        # one lockfile locks and unlocks all of them together.
        sample_ids = ["SCPCS999990", "SCPCS999991", "SCPCS999997"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            Sample.sync_model()
            Sample.sync_metadata()

        OriginalFileFactory(project_id="SCPCP999990", is_lockfile=True)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()

        self.assertEqual(output_counts["locked"], 3)
        non_tainted_sample = Sample.objects.get(scpca_id="SCPCS999990")
        tainted_original_files_sample = Sample.objects.get(scpca_id="SCPCS999991")
        tainted_metadata_sample = Sample.objects.get(scpca_id="SCPCS999997")
        self.assertEqual(non_tainted_sample.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_original_files_sample.loaded_state, LoadableResourceStates.LOCKED)
        self.assertEqual(tainted_metadata_sample.loaded_state, LoadableResourceStates.LOCKED)

        mutated_file = OriginalFile.objects.filter(sample_ids__contains=["SCPCS999991"]).first()
        mutated_file.hash = "mutated_hash_value"
        mutated_file.save(update_fields=["hash"])

        OriginalFile.objects.filter(project_id="SCPCP999990", is_lockfile=True).delete()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(
                Sample,
                sample_ids,
                modified_resource_id="SCPCS999997",
                mutated_field="diagnosis",
                mutated_value="Mutated diagnosis",
            ),
        ):
            output_counts = Sample.sync_model()

        non_tainted_sample.refresh_from_db()
        tainted_original_files_sample.refresh_from_db()
        tainted_metadata_sample.refresh_from_db()
        self.assertEqual(non_tainted_sample.loaded_state, LoadableResourceStates.SYNCED)
        self.assertEqual(tainted_original_files_sample.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(tainted_metadata_sample.loaded_state, LoadableResourceStates.TAINTED)
        self.assertEqual(output_counts["locked"], 0)
        self.assertEqual(output_counts["unlocked"], 1)
        self.assertEqual(output_counts["tainted"], 2)

    def test_sync_model_purge_deleted_sample(self):
        sample_ids = ["SCPCS999996"]
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        Project.sync_model()
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            Sample.sync_model()
        self.assertTrue(Sample.objects.filter(scpca_id="SCPCS999996").exists())

        # Assert OF deletion with sample still in metadata preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, sample_ids),
        ):
            output_counts = Sample.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Sample.objects.filter(scpca_id="SCPCS999996").exists())

        # Assert deletion in metadata but lack of OF deletion preserves object in db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, sample_ids),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, []),
        ):
            output_counts = Sample.sync_model()

        self.assertEqual(output_counts["deleted"], 0)
        self.assertTrue(Sample.objects.filter(scpca_id="SCPCS999996").exists())

        # Assert satisfaction of both conditions yields purged object from db
        with patch(
            "scpca_portal.models.OriginalFile.get_syncable_files",
            side_effect=filter_original_files_by_resource_wrapper(Sample, []),
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        with patch(
            "scpca_portal.metadata_parser.load_all_samples_metadata",
            side_effect=filter_metadata_by_resource_wrapper(Sample, []),
        ):
            output_counts = Sample.sync_model()

        self.assertEqual(output_counts["deleted"], 1)
        self.assertFalse(Sample.objects.filter(scpca_id="SCPCS999996").exists())

    # SYNC_METADATA TESTS
    def test_sync_metadata(self):
        pass
