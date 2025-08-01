from django.test import TestCase

from pydantic import ValidationError

from scpca_portal.enums import Modalities
from scpca_portal.validators import DatasetDataModel, ProjectDataModel


class TestProjectDataModel(TestCase):
    def test_valid_single_cell_list(self):
        project_data = {
            "includes_bulk": True,
            Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999992"],
            Modalities.SPATIAL.value: ["SCPCS999991"],
        }
        validated_project_data = ProjectDataModel.model_validate(project_data)

        expected_single_cell_ids = ["SCPCS999990", "SCPCS999992"]
        self.assertEqual(validated_project_data.SINGLE_CELL, expected_single_cell_ids)

    def test_valid_single_cell_merged_string(self):
        project_data = {
            "includes_bulk": False,
            Modalities.SINGLE_CELL.value: "MERGED",
            Modalities.SPATIAL.value: [],
        }
        validated_project_data = ProjectDataModel.model_validate(project_data)
        self.assertEqual(validated_project_data.SINGLE_CELL, "MERGED")

    def test_invalid_single_cell_sample_id(self):
        project_data = {Modalities.SINGLE_CELL.value: ["INVALID_SAMPLE_ID"]}
        with self.assertRaises(ValidationError) as context:
            ProjectDataModel.model_validate(project_data)
        self.assertIn("Invalid sample ID format", str(context.exception))

    def test_invalid_single_cell_sample_id_passed_as_string(self):
        project_data = {Modalities.SINGLE_CELL.value: "SCPCS999990"}
        with self.assertRaises(ValidationError) as context:
            ProjectDataModel.model_validate(project_data)
        self.assertIn("Sample IDs must be inside an Array", str(context.exception))

    def test_invalid_single_cell_merged_string(self):
        project_data = {Modalities.SINGLE_CELL.value: "NOT_MERGED"}
        with self.assertRaises(ValidationError) as context:
            ProjectDataModel.model_validate(project_data)
        self.assertIn("Invalid string value for 'single-cell' modality", str(context.exception))

    def test_invalid_spatial_sample_id(self):
        project_data = {Modalities.SPATIAL.value: ["INVALID_SAMPLE_ID"]}
        with self.assertRaises(ValidationError) as context:
            ProjectDataModel.model_validate(project_data)
        self.assertIn("Invalid sample ID format", str(context.exception))


class TestDatasetDataModel(TestCase):
    def test_valid_dataset_data(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999992"],
                Modalities.SPATIAL.value: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
        }
        validated_data = DatasetDataModel.model_validate(data)
        self.assertIn("SCPCP999990", validated_data.root)
        self.assertEqual(validated_data.root["SCPCP999991"].SINGLE_CELL, "MERGED")

    def test_invalid_project_id(self):
        data = {"INVALID_PROJECT_ID": {Modalities.SINGLE_CELL.value: ["SCPCS999990"]}}
        with self.assertRaises(ValidationError) as context:
            DatasetDataModel.model_validate(data)
        self.assertIn("Invalid project ID format", str(context.exception))

    def test_invalid_nested_sample_id(self):
        data = {"SCPCP999990": {Modalities.SINGLE_CELL.value: ["INVALID_SAMPLE_ID"]}}
        with self.assertRaises(ValidationError) as context:
            DatasetDataModel.model_validate(data)

        self.assertIn("Invalid sample ID format", str(context.exception))
