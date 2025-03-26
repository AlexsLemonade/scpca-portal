from functools import partial
from typing import Any, Dict

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag

from scpca_portal import loader
from scpca_portal.enums import Modalities
from scpca_portal.models import Dataset, Project
from scpca_portal.test.expected_values import test_dataset as test_data
from scpca_portal.test.factories import DatasetFactory


class TestDatasetUnit(TestCase):
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
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Incorrect project ids
        data = {
            "project_id": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Lack of SCPCP prefix
        data = {
            "SCPCA999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Incorrect number of digits
        data = {
            "SCPCP9999900": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
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
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
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
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": "True",
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": "True",
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: "SCPCS999990",
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: [1, 2, 3],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["sample_id"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: "SCPCS999992",
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: [1, 2, 3],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["sample_id"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

    def test_is_ccdl_default_set(self):
        dataset = DatasetFactory()
        self.assertFalse(dataset.is_ccdl)


class TestDatasetIntegration(TestCase):
    def setUp(self):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        # When passing a project_id to get_projects_metadata, a list of one item is returned
        # This lambda creates a shorthand with which to access the single returned project_metadata
        self.get_project_metadata = lambda project_id: loader.get_projects_metadata(
            filter_on_project_id=project_id
        )[0]

        self.create_project = partial(
            loader.create_project,
            submitter_whitelist={"scpca"},
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            reload_existing=True,
            update_s3=False,
        )

    def assertObjectProperties(self, obj: Any, expected_values: Dict[str, Any]) -> None:
        for attribute, value in expected_values.items():
            msg = f"The actual and expected `{attribute}` values differ in {obj}"
            if isinstance(value, list):
                self.assertListEqual(getattr(obj, attribute), value, msg)
            else:
                self.assertEqual(getattr(obj, attribute), value, msg)

    def test_get_or_find_ccdl_dataset_SINGLE_CELL_SCE(self):
        # PROJECT CCDL DATASET
        project = self.create_project(
            self.get_project_metadata(test_data.CCDLDatasetProject.SINGLE_CELL_SCE.PROJECT_ID)
        )
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_get_ccdl_dataset_"
            f"{test_data.CCDLDatasetProject.SINGLE_CELL_SCE.CCDL_NAME}",
        )

        dataset, is_new_dataset = Dataset.get_or_find_ccdl_dataset(
            test_data.CCDLDatasetProject.SINGLE_CELL_SCE.CCDL_NAME, project.scpca_id
        )
        dataset.save()
        self.assertTrue(is_new_dataset)
        self.assertObjectProperties(dataset, test_data.CCDLDatasetProject.SINGLE_CELL_SCE.VALUES)

        dataset, is_new_dataset = Dataset.get_or_find_ccdl_dataset(
            test_data.CCDLDatasetPortal.SINGLE_CELL_SCE.CCDL_NAME, project.scpca_id
        )
        self.assertFalse(is_new_dataset)
        Project.objects.all().delete()

        # PORTAL WIDE CCDL DATASET
        for project in loader.get_projects_metadata():
            self.create_project(project)

        # Make sure that create_project didn't fail and didn't create the intended projects
        self.assertEqual(
            Project.objects.count(),
            3,
            "Problem creating projects, unable to test "
            "test_get_ccdl_dataset_"
            f"{test_data.CCDLDatasetPortal.SINGLE_CELL_SCE.CCDL_NAME}",
        )

        dataset, is_new_dataset = Dataset.get_or_find_ccdl_dataset(
            test_data.CCDLDatasetPortal.SINGLE_CELL_SCE.CCDL_NAME
        )
        dataset.save()
        self.assertTrue(is_new_dataset)
        self.assertObjectProperties(dataset, test_data.CCDLDatasetPortal.SINGLE_CELL_SCE.VALUES)

        dataset, is_new_dataset = Dataset.get_or_find_ccdl_dataset(
            test_data.CCDLDatasetProject.SINGLE_CELL_SCE.CCDL_NAME
        )
        self.assertFalse(is_new_dataset)
