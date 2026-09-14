from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Sample
from scpca_portal.test.factories import (
    LeafProjectFactory,
    LibraryFactory,
    OriginalFileFactory,
    SampleFactory,
)


class TestSample(TestCase):
    def test_sync_metadata(self):
        original_loaded_at_timestamp = make_aware(datetime.now())

        new_sample = SampleFactory(loaded_state=LoadableResourceStates.NEW)
        tainted_sample = SampleFactory(
            loaded_state=LoadableResourceStates.TAINTED, loaded_at=original_loaded_at_timestamp
        )
        # synced sample should be left untouched
        synced_sample = SampleFactory(
            loaded_state=LoadableResourceStates.SYNCED, loaded_at=original_loaded_at_timestamp
        )

        updatable_samples = [new_sample, tainted_sample]

        metadata_by_id = {
            new_sample.scpca_id: {
                "scpca_sample_id": new_sample.scpca_id,
                "age": "8",
                "age_timing": "early",
                "diagnosis": "medulloblastoma",
                "subdiagnosis": "NA",
            },
            tainted_sample.scpca_id: {
                "scpca_sample_id": tainted_sample.scpca_id,
                "age": "12",
                "age_timing": "late",
                "diagnosis": "ependymoma",
                "subdiagnosis": "NA",
            },
        }

        with patch.object(
            Sample, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            Sample.sync_metadata()

            # verify inputs (only NEW and TAINTED resources are passed through for metadata lookup)
            mock_get_metadata.assert_called_once()
            resources_arg = mock_get_metadata.call_args.kwargs["resources"]
            self.assertListEqual(
                sorted([sample.scpca_id for sample in resources_arg]),
                sorted([new_sample.scpca_id, tainted_sample.scpca_id]),
            )

            # verify outputs
            # (each sample is updated from its own metadata dict, marked synced, and persisted)
            for sample in updatable_samples:
                sample.refresh_from_db()

            self.assertEqual(new_sample.age, "8")
            self.assertEqual(new_sample.diagnosis, "medulloblastoma")
            self.assertEqual(new_sample.subdiagnosis, "NA")

            self.assertEqual(tainted_sample.age, "12")
            self.assertEqual(tainted_sample.diagnosis, "ependymoma")
            self.assertEqual(tainted_sample.subdiagnosis, "NA")

            for sample in updatable_samples:
                self.assertEqual(sample.loaded_state, LoadableResourceStates.SYNCED)
                self.assertGreater(sample.loaded_at, original_loaded_at_timestamp)

            # verify synced sample was not touched
            synced_sample.refresh_from_db()
            self.assertEqual(synced_sample.loaded_at, original_loaded_at_timestamp)

    def test_sync_metadata_no_updatable_resource(self):
        SampleFactory(loaded_state=LoadableResourceStates.SYNCED)

        with patch.object(Sample, "get_metadata_dicts_by_id") as mock_get_metadata:
            Sample.sync_metadata()

        mock_get_metadata.assert_not_called()

    def test_sync_model(self):
        project = LeafProjectFactory()

        # DELETED: no longer referenced by any original file, and isn't in current metadata
        to_be_deleted_sample = SampleFactory(project=project)

        # CREATED: only referenced by incoming metadata, doesn't exist in the DB yet
        new_sample_id = "SCPCS999901"

        # LOCKED: its project has a lockfile in the input bucket
        locked_project = LeafProjectFactory()
        newly_locked_sample = SampleFactory(
            project=locked_project, loaded_state=LoadableResourceStates.SYNCED
        )
        OriginalFileFactory(project_id=locked_project.scpca_id, is_lockfile=True)

        # UNLOCKED & SYNCED: was locked, its project's lockfile has since been removed,
        # and its metadata is unchanged
        unlocked_synced_sample = SampleFactory(
            project=project,
            loaded_state=LoadableResourceStates.LOCKED,
            loaded_at=make_aware(datetime.now()),
        )
        unlocked_synced_metadata = {
            "scpca_sample_id": unlocked_synced_sample.scpca_id,
            "age": "8",
        }
        unlocked_synced_sample.combined_hash = unlocked_synced_sample.get_current_combined_hash(
            unlocked_synced_metadata
        )
        unlocked_synced_sample.save(update_fields=["combined_hash"])

        # UNLOCKED & TAINTED: was locked, its project's lockfile has since been removed,
        # and its metadata has changed
        unlocked_tainted_sample = SampleFactory(
            project=project,
            loaded_state=LoadableResourceStates.LOCKED,
            loaded_at=make_aware(datetime.now()),
            combined_hash="outdated_combined_hash",
        )
        unlocked_tainted_metadata = {
            "scpca_sample_id": unlocked_tainted_sample.scpca_id,
            "age": "12",
        }

        metadata_by_id = {
            new_sample_id: {
                "scpca_project_id": project.scpca_id,
                "scpca_sample_id": new_sample_id,
            },
            # present so it survives remove_deleted_objects; locking doesn't need its metadata
            newly_locked_sample.scpca_id: {
                "scpca_project_id": locked_project.scpca_id,
                "scpca_sample_id": newly_locked_sample.scpca_id,
            },
            unlocked_synced_sample.scpca_id: unlocked_synced_metadata,
            unlocked_tainted_sample.scpca_id: unlocked_tainted_metadata,
        }

        with patch.object(
            Sample, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            output_counts = Sample.sync_model()

        # verify inputs
        mock_get_metadata.assert_called_once_with(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, skip_existing_file_download=False
        )

        # verify outputs
        self.assertDictEqual(
            output_counts,
            {"created": 1, "deleted": 1, "locked": 1, "unlocked": 1, "tainted": 1},
        )

        self.assertFalse(Sample.objects.filter(scpca_id=to_be_deleted_sample.scpca_id).exists())
        self.assertTrue(Sample.objects.filter(scpca_id=new_sample_id, project=project).exists())

        newly_locked_sample.refresh_from_db()
        self.assertEqual(newly_locked_sample.loaded_state, LoadableResourceStates.LOCKED)

        unlocked_synced_sample.refresh_from_db()
        self.assertEqual(unlocked_synced_sample.loaded_state, LoadableResourceStates.SYNCED)

        unlocked_tainted_sample.refresh_from_db()
        self.assertEqual(unlocked_tainted_sample.loaded_state, LoadableResourceStates.TAINTED)

    def test_sync_model_no_changes(self):
        with patch.object(Sample, "get_metadata_dicts_by_id", return_value={}):
            output_counts = Sample.sync_model()

        self.assertDictEqual(
            output_counts,
            {"created": 0, "deleted": 0, "locked": 0, "unlocked": 0, "tainted": 0},
        )

    def test_sync_aggregations(self):
        # bulk is turned off for now, the bulk path will be tested when actual test data is used
        project = LeafProjectFactory(has_bulk_rna_seq=False)

        stale_sample = SampleFactory(
            project=project, aggregation_hash="stale_hash", seq_units=["placeholder"]
        )
        stale_library = LibraryFactory(project=project, metadata_hash="library_hash")
        stale_sample.libraries.add(stale_library)

        # placeholder seq_units proves this sample's aggregations are left untouched
        up_to_date_sample = SampleFactory(project=project, seq_units=["placeholder"])
        up_to_date_library = LibraryFactory(project=project, metadata_hash="library_hash_2")
        up_to_date_sample.libraries.add(up_to_date_library)
        up_to_date_sample.aggregation_hash = up_to_date_sample.current_aggregation_hash
        up_to_date_sample.save(update_fields=["aggregation_hash"])

        resources = Sample.objects.filter(id__in=[stale_sample.id, up_to_date_sample.id])
        Sample.sync_aggregations(resources)

        stale_sample.refresh_from_db()
        up_to_date_sample.refresh_from_db()

        # stale sample's aggregations were recomputed and its hash brought up to date
        self.assertEqual(stale_sample.aggregation_hash, stale_sample.current_aggregation_hash)
        self.assertEqual(stale_sample.seq_units, ["cell"])

        # up-to-date sample was left untouched
        self.assertEqual(up_to_date_sample.seq_units, ["placeholder"])

    def test_sync_aggregations_no_changes(self):
        project = LeafProjectFactory(has_bulk_rna_seq=False)
        sample = SampleFactory(project=project, seq_units=["placeholder"])
        sample.aggregation_hash = sample.current_aggregation_hash
        sample.save(update_fields=["aggregation_hash"])

        Sample.sync_aggregations(Sample.objects.filter(id=sample.id))

        sample.refresh_from_db()
        self.assertEqual(sample.seq_units, ["placeholder"])
