from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Sample
from scpca_portal.test.factories import SampleFactory


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
