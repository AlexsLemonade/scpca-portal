from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.enums import DatasetFormats, FileFormats, Modalities
from scpca_portal.models import CCDLDataset, ComputedFile, Project
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import (
    CCDLDatasetFactory,
    LeafComputedFileFactory,
    LibraryFactory,
    OriginalFileFactory,
    SampleFactory,
)


class TestCCDLDataset(TestCase):
    @classmethod
    def setUpTestData(cls):
        bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        call_command("sync_original_files", bucket=bucket)

        loader.download_projects_metadata()
        project_ids = metadata_parser.get_projects_metadata_ids(bucket=bucket)

        loader.download_projects_related_metadata(project_ids)
        for project_metadata in metadata_parser.load_projects_metadata(project_ids):
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=bucket,
                reload_existing=True,
                update_s3=False,
            )

    def test_get_or_find(self):
        # Portal Dataset Check
        ccdl_portal_datasets_expected_values = [
            test_data.DatasetAllMetadata,
            test_data.DatasetSingleCellSingleCellExperiment,
            test_data.DatasetSingleCellSingleCellExperimentMerged,
            test_data.DatasetSingleCellAnndata,
            test_data.DatasetSingleCellAnndataMerged,
            test_data.DatasetSpatialSpatialSpaceranger,
        ]

        for ccdl_portal_dataset in ccdl_portal_datasets_expected_values:
            dataset, found = CCDLDataset.get_or_find(ccdl_portal_dataset.CCDL_NAME)
            dataset.save()
            self.assertFalse(found)

            for attribute, value in ccdl_portal_dataset.VALUES.items():
                msg = f"The actual and expected `{attribute}` values differ in {dataset}"
                if isinstance(value, list):
                    self.assertListEqual(getattr(dataset, attribute), value, msg)
                else:
                    self.assertEqual(getattr(dataset, attribute), value, msg)

            dataset_same, found_same = CCDLDataset.get_or_find(ccdl_portal_dataset.CCDL_NAME)
            self.assertEqual(dataset_same.pk, dataset.pk)
            self.assertTrue(found_same)

        # Project Dataset Check
        ccdl_project_dataset = (
            test_data.DatasetSingleCellSingleCellExperimentNoMultiplexedSCPCP999991
        )
        dataset, found = CCDLDataset.get_or_find(
            ccdl_project_dataset.CCDL_NAME, ccdl_project_dataset.PROJECT_ID
        )
        dataset.save()
        self.assertFalse(found)

        for attribute, value in ccdl_project_dataset.VALUES.items():
            msg = f"The actual and expected `{attribute}` values differ in {dataset}"
            if isinstance(value, list):
                self.assertListEqual(getattr(dataset, attribute), value, msg)
            else:
                self.assertEqual(getattr(dataset, attribute), value, msg)

        dataset, found = CCDLDataset.get_or_find(
            ccdl_project_dataset.CCDL_NAME, ccdl_project_dataset.PROJECT_ID
        )
        self.assertTrue(found)

    def test_create_or_update_ccdl_datasets(self):
        # There are 21 total datasets created
        #     CCDL DATASET TYPE              Total   Projects   Portal Wide
        #   - ALL_METADATA                   4       3          Yes
        #   - SINGLE_CELL_SCE                4       3          Yes
        #   - SINGLE_CELL_SCE_NO_MULTIPLEXED 1       1          No
        #   - SINGLE_CELL_SCE_MERGED         3       2          Yes
        #   - SINGLE_CELL_ANN_DATA           4       3          Yes
        #   - SINGLE_CELL_ANN_DATA_MERGED    3       2          Yes
        #   - SPATIAL_SCE                    2       1          Yes

        # Initial call
        created_datasets, updated_datasets = CCDLDataset.create_or_update_ccdl_datasets()
        self.assertEqual(len(created_datasets), 21)
        self.assertEqual(len(updated_datasets), 0)

        # Call again
        created_datasets, updated_datasets = CCDLDataset.create_or_update_ccdl_datasets()
        self.assertEqual(len(created_datasets), 0)
        self.assertEqual(len(updated_datasets), 0)

        # Call with ignore_hash
        created_datasets, updated_datasets = CCDLDataset.create_or_update_ccdl_datasets(
            ignore_hash=True
        )
        self.assertEqual(len(created_datasets), 0)
        self.assertEqual(len(updated_datasets), 21)

    def test_create_or_update_ccdl_datasets_update_data_attr(self):
        """Assert that data attr updates when new samples and libraries are added."""
        # Create dataset
        dataset_expected_values = test_data.DatasetSingleCellSingleCellExperimentSCPCP999990
        dataset, _ = CCDLDataset.get_or_find(
            dataset_expected_values.CCDL_NAME, dataset_expected_values.PROJECT_ID
        )
        dataset.save()

        # Define original and expected values
        actual_old_data_attr = dataset.current_data
        expected_old_data_attr = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            }
        }
        expected_new_data_attr = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997", "SCPCS999999"],
                Modalities.SPATIAL: [],
            }
        }

        # Simulate the work of sync_original_files and load_metadata commands
        # with a new sample and library added to an existing project
        project_id, sample_id, library_id = "SCPCP999990", "SCPCS999999", "SCPCL999999"
        OriginalFileFactory(
            s3_key="SCPCP999990/SCPCS999999/SCPCL999999.rds",
            project_id=project_id,
            sample_ids=[sample_id],
            library_id=library_id,
            is_single_cell=True,
            is_single_cell_experiment=True,
            formats=[FileFormats.SINGLE_CELL_EXPERIMENT],
        )

        project = Project.objects.filter(scpca_id=project_id).first()
        sample = SampleFactory(scpca_id=sample_id, has_single_cell_data=True, project=project)
        sample.save()

        library = LibraryFactory(
            scpca_id=library_id, modality=Modalities.SINGLE_CELL, project=project
        )
        library.samples.add(sample)
        library.save()

        # Rerun create update ccdl datasets method
        _, updated_datasets = CCDLDataset.create_or_update_ccdl_datasets()
        updated_dataset = updated_datasets[0]
        actual_new_data_attr = updated_dataset.data

        # Make assertions
        self.assertEqual(actual_old_data_attr, expected_old_data_attr)
        self.assertEqual(actual_new_data_attr, expected_new_data_attr)
        self.assertNotEqual(actual_old_data_attr, actual_new_data_attr)

    @patch("scpca_portal.models.computed_file.utils.get_today_string", return_value="2025-08-26")
    @patch("scpca_portal.s3.aws_s3.generate_presigned_url")
    def test_download_url_property(self, mock_generate_presigned_url, _):
        # ccdl project dataset
        dataset = CCDLDatasetFactory(
            ccdl_project_id="SCPCP999990", format=DatasetFormats.SINGLE_CELL_EXPERIMENT
        )
        dataset.computed_file = LeafComputedFileFactory(
            s3_key=ComputedFile.get_dataset_file_s3_key(dataset)
        )
        dataset.save()

        dataset.download_url
        expected_filename = "SCPCP999990_single-cell-experiment_2025-08-26.zip"
        mock_generate_presigned_url.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": "scpca-portal-local",
                "Key": f"{dataset.id}.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        # ccdl portal wide dataset
        dataset = CCDLDatasetFactory(
            ccdl_project_id=None, format=DatasetFormats.SINGLE_CELL_EXPERIMENT
        )
        dataset.computed_file = LeafComputedFileFactory(
            s3_key=ComputedFile.get_dataset_file_s3_key(dataset)
        )
        dataset.save()

        dataset.download_url
        expected_filename = "portal-wide_single-cell-experiment_2025-08-26.zip"
        mock_generate_presigned_url.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": "scpca-portal-local",
                "Key": f"{dataset.id}.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        # no computed file
        dataset = CCDLDatasetFactory()
        self.assertIsNone(dataset.download_url)
