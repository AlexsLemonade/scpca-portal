from django.test import TestCase

from scpca_portal.enums import DatasetFormats, Modalities
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

    def test_change_format_with_empty_data(self):
        serializer = DatasetUpdateSerializer(instance=self.dataset_empty, data=self.incoming_data)
        # Changing format passes when dataset.data is empty
        self.assertTrue(serializer.is_valid())
        modified_dataset = serializer.save()
        self.assertEqual(modified_dataset.format, DatasetFormats.ANN_DATA)

    def test_change_format_with_data(self):
        serializer = DatasetUpdateSerializer(
            instance=self.dataset_with_data, data=self.incoming_data
        )
        # Changing format fails when dataset.data is not empty
        self.assertFalse(serializer.is_valid())

        expected_error = "Dataset with data cannot change format."
        self.assertIn(expected_error, serializer.errors["format"]["detail"])
