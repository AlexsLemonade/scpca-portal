from django.test import TestCase

from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.exceptions import UpdateProcessingDatasetError
from scpca_portal.test.factories import DatasetFactory
from scpca_portal.views.dataset import DatasetUpdateSerializer


class TestDatasetSerializer(TestCase):
    def setUp(self):
        self.incoming_data = {"format": DatasetFormats.ANN_DATA}
        self.dataset_empty = DatasetFactory(format=DatasetFormats.SINGLE_CELL_EXPERIMENT, data={})
        self.dataset_with_data = DatasetFactory(
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
            data={
                "SCPCP999990": {
                    "includes_bulk": False,
                    Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL: [],
                },
            },
        )
        self.dataset_processing = DatasetFactory(
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT, start=True
        )

    def test_change_format_with_empty_data(self):
        serializer = DatasetUpdateSerializer(instance=self.dataset_empty, data=self.incoming_data)
        # Format change allowed only if data is empty
        self.assertTrue(serializer.is_valid())
        modified_dataset = serializer.save()
        self.assertEqual(modified_dataset.format, DatasetFormats.ANN_DATA)

    def test_change_format_with_data(self):
        serializer = DatasetUpdateSerializer(
            instance=self.dataset_with_data, data=self.incoming_data
        )
        # Format change not allowed for datasets containing data
        self.assertFalse(serializer.is_valid())

        expected_error = "Dataset with data cannot change format."
        self.assertIn(expected_error, serializer.errors["format"]["detail"])

    def test_change_format_when_processing(self):
        serializer = DatasetUpdateSerializer(
            instance=self.dataset_processing, data=self.incoming_data
        )
        # No Format change allowed for processing datasets
        with self.assertRaises(UpdateProcessingDatasetError) as context:
            serializer.is_valid(raise_exception=True)

        expected_status = 409
        expected_error = "Invalid request: Processing datasets cannot be modified."
        self.assertEqual(context.exception.status_code, expected_status)
        self.assertEqual(str(context.exception.detail), expected_error)
