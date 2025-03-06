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

    @tag("is_data_valid")
    def test_is_data_valid_project_id(self):
        # Valid project id
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Incorrect project ids
        data = {
            "project_id": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Lack of SCPCP prefix
        data = {
            "SCPCA999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Incorrect number of digits
        data = {
            "SCPCP9999900": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

    @tag("is_data_valid")
    def test_is_data_valid_config(self):
        # Valid config
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Empty config (valid)
        data = {
            "SCPCP999990": {},
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - missing (valid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": "True",
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": "True",
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "SCPCS999990",
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [1, 2, 3],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["sample_id"],
                Modalities.SPATIAL: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: "SCPCS999992",
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: [1, 2, 3],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["sample_id"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)
