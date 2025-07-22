from django.test import TestCase

from pydantic import ValidationError

from scpca_portal.validators import DatasetData, ProjectData


class TestProjectData(TestCase):
    def test_valid_single_cell_list(self):
        project_data = {
            "includes_bulk": True,
            "single_cell": ["SCPCS999990", "SCPCS999992"],
            "spatial": ["SCPCS999991"],
        }
        validated_project_data = ProjectData.model_validate(project_data)

        expected_single_cell_ids = ["SCPCS999990", "SCPCS999992"]
        self.assertEqual(validated_project_data.single_cell, expected_single_cell_ids)

    def test_valid_single_cell_merged_string(self):
        project_data = {"includes_bulk": False, "single_cell": "MERGED", "spatial": []}
        validated_project_data = ProjectData.model_validate(project_data)
        self.assertEqual(validated_project_data.single_cell, "MERGED")

    def test_invalid_single_cell_sample_id(self):
        project_data = {"single_cell": ["INVALID_SAMPLE_ID"]}
        with self.assertRaises(ValidationError) as context:
            ProjectData.model_validate(project_data)
        self.assertIn("Invalid sample ID format", str(context.exception))

    def test_invalid_single_cell_merged_string(self):
        project_data = {"single_cell": "NOT_MERGED"}
        with self.assertRaises(ValidationError) as context:
            ProjectData.model_validate(project_data)
        self.assertIn("Invalid string value for 'single-cell' modality", str(context.exception))

    def test_invalid_spatial_sample_id(self):
        project_data = {"spatial": ["INVALID_SAMPLE_ID"]}
        with self.assertRaises(ValidationError) as context:
            ProjectData.model_validate(project_data)
        self.assertIn("Invalid sample ID format", str(context.exception))


class TestDatasetData(TestCase):
    def test_valid_dataset_data(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                "single_cell": ["SCPCS999990", "SCPCS999992"],
                "spatial": ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                "single_cell": "MERGED",
                "spatial": [],
            },
        }
        validated_data = DatasetData.model_validate(data)
        self.assertIn("SCPCP999990", validated_data.root)
        self.assertEqual(validated_data.root["SCPCP999991"].single_cell, "MERGED")

    def test_invalid_project_id(self):
        data = {"INVALID_PROJECT_ID": {"single_cell": ["SCPCS999990"]}}
        with self.assertRaises(ValidationError) as context:
            DatasetData.model_validate(data)
        self.assertIn("Invalid project ID format", str(context.exception))

    def test_invalid_nested_sample_id(self):
        data = {"SCPCP999990": {"single_cell": ["INVALID_SAMPLE_ID"]}}
        with self.assertRaises(ValidationError) as context:
            DatasetData.model_validate(data)

        self.assertIn("Invalid sample ID format", str(context.exception))
