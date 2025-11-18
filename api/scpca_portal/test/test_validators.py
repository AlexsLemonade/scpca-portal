from django.test import TestCase

from pydantic import ValidationError

from scpca_portal.enums import Modalities
from scpca_portal.test.factories import ProjectFactory, SampleFactory
from scpca_portal.validators import DatasetDataModel, DatasetDataModelRelations, ProjectDataModel


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

    def test_valid_single_cell_list_with_missing_keys(self):
        project_data = {
            Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999992"],
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

    def test_valid_bulk_string(self):
        project_data = {
            "includes_bulk": "True",
            Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999992"],
            Modalities.SPATIAL.value: ["SCPCS999991"],
        }
        validated_project_data = ProjectDataModel.model_validate(project_data)
        self.assertTrue(validated_project_data.includes_bulk)

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


class TestDatasetDataModelRelations(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = ProjectFactory(scpca_id="SCPCP000001", sample=None)
        SampleFactory(scpca_id="SCPCS000001", project=cls.project, has_single_cell_data=True)
        SampleFactory(scpca_id="SCPCS000002", project=cls.project, has_single_cell_data=True)
        SampleFactory(scpca_id="SCPCS000003", project=cls.project, has_spatial_data=True)

    def test_validate_projects(self):
        # no exceptions thrown
        data = {
            "SCPCP000001": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: ["SCPCS000001", "SCPCS000002"],
                Modalities.SPATIAL.value: ["SCPCS000003"],
            },
        }

        DatasetDataModelRelations.validate_projects(data)  # no exception should be thrown here

        # assert project id doesn't exist
        data = {
            "SCPCP999999": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: ["SCPCS000001", "SCPCS000002"],
                Modalities.SPATIAL.value: ["SCPCS000003"],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_projects(data)
        self.assertEqual(str(e.exception), "The following projects do not exist: SCPCP999999")

        # assert merged can't be requested from project without merged files
        self.project.includes_merged_sce = False
        self.project.save()
        data = {
            "SCPCP000001": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_projects(data)
        self.assertEqual(
            str(e.exception), "The following projects do not have merged files: SCPCP000001"
        )

        # assert merged can be requested from project with merged files
        self.project.includes_merged_sce = True
        self.project.save()
        data = {
            "SCPCP000001": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
        }

        DatasetDataModelRelations.validate_projects(data)  # no exception thrown

        # assert bulk can't be requested from project without bulk data
        self.project.has_bulk_rna_seq = False
        self.project.save()
        data = {
            "SCPCP000001": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS000001", "SCPCS000002"],
                Modalities.SPATIAL.value: ["SCPCS000003"],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_projects(data)
        self.assertEqual(
            str(e.exception), "The following projects do not have bulk data: SCPCP000001"
        )

        # assert bulk can be requested from project with bulk data
        self.project.has_bulk_rna_seq = True
        self.project.save()
        data = {
            "SCPCP000001": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS000001", "SCPCS000002"],
                Modalities.SPATIAL.value: ["SCPCS000003"],
            },
        }

        DatasetDataModelRelations.validate_projects(data)  # no exception thrown

    def test_validate_samples(self):
        # assert sample ids doesn't exist
        data = {
            "SCPCP000001": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS000004", "SCPCS000005"],
                Modalities.SPATIAL.value: ["SCPCS000006"],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_samples(data)
        self.assertEqual(
            str(e.exception),
            "The following samples do not exist: SCPCS000004, SCPCS000005, SCPCS000006",
        )

        # assert spatial sample isn't associated with single cell modality
        data = {
            "SCPCP000001": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: ["SCPCS000003"],
                Modalities.SPATIAL.value: [],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_samples(data)
        self.assertEqual(
            str(e.exception),
            "The following samples are not associated with SCPCP000001 and SINGLE_CELL: "
            "SCPCS000003",
        )

        # assert that a sample isn't associated with its project
        ProjectFactory(scpca_id="SCPCP000002", sample=None)
        data = {
            "SCPCP000002": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: ["SCPCS000001", "SCPCS000002"],
                Modalities.SPATIAL.value: [],
            },
        }

        with self.assertRaises(Exception) as e:
            DatasetDataModelRelations.validate_samples(data)

        self.assertEqual(
            str(e.exception),
            "The following samples are not associated with SCPCP000002 and SINGLE_CELL: "
            "SCPCS000001, SCPCS000002",
        )

        # assert that a sample can be both single cell and spatial
        project = ProjectFactory(scpca_id="SCPCP000003", sample=None)
        SampleFactory(
            scpca_id="SCPCS000010",
            project=project,
            has_single_cell_data=True,
            has_spatial_data=True,
        )
        data = {
            "SCPCP000003": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS000010"],
                Modalities.SPATIAL.value: ["SCPCS000010"],
            },
        }

        # no exception raised
        DatasetDataModelRelations.validate_samples(data)
