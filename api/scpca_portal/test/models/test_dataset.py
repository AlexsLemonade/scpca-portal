from django.test import TestCase, tag

from scpca_portal.enums import Modalities
from scpca_portal.models import Dataset
from scpca_portal.test.factories import DatasetFactory


class TestDataset(TestCase):
    def test_dataset_saved_to_db(self):
        dataset = DatasetFactory()
        self.assertEqual(Dataset.objects.count(), 1)

        returned_dataset = Dataset.objects.filter(pk=dataset.id).first()
        self.assertEqual(returned_dataset, dataset)

    @tag("validate_data")
    def test_validate_data_project_id(self):
        # Valid project id
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(Dataset.validate_data(data))

        # Incorrect project ids
        data = {
            "project_id": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Lack of SCPCP prefix
        data = {
            "SCPCA999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Incorrect number of digits
        data = {
            "SCPCP9999900": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

    @tag("validate_data")
    def test_validate_data_config(self):
        # Valid config
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(Dataset.validate_data(data))

        # Empty config
        data = {
            "SCPCP999990": {},
        }
        self.assertFalse(Dataset.validate_data(data))

        # Merge single cell - missing
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Merge single cell - wrong data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": "True",
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Includes bulk - missing
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Includes bulk - wrong data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": "True",
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Single Cell - missing
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Single Cell - wrong data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "SCPCS999990",
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Single Cell - wrong inner data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [1, 2, 3],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Single Cell - invalid sample id
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["sample_id"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Spatial - missing
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Spatial - wrong data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: "SCPCS999992",
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Spatial - wrong inner data type
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: [1, 2, 3],
            },
        }
        self.assertFalse(Dataset.validate_data(data))

        # Spatial - invalid sample id
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["sample_id"],
            },
        }
        self.assertFalse(Dataset.validate_data(data))
