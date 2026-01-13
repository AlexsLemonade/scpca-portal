from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser, utils
from scpca_portal.enums import CCDLDatasetNames
from scpca_portal.models import CCDLDataset, ComputedFile, UserDataset
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import LibraryFactory, ProjectFactory, SampleFactory


class TestComputedFile(TestCase):
    @patch("scpca_portal.models.computed_file.utils.get_today_string", return_value="2024-01-18")
    @patch("scpca_portal.s3.aws_s3.generate_presigned_url")
    def test_computed_file_create_download_url(self, s3_endpoint, _):
        computed_file = ComputedFile(
            format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key="SCPCP000001.zip",
            size_in_bytes=10000,
            workflow_version="v1.0",
        )

        computed_file.download_url
        expected_filename = "SCPCP000001_2024-01-18.zip"
        s3_endpoint.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": computed_file.s3_bucket,
                "Key": "SCPCP000001.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=604800,
        )


class TestGetFile(TestCase):
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

    def setUp(self) -> None:
        self.project = ProjectFactory()
        LibraryFactory(project=self.project)

        self.sample = SampleFactory()
        sample_library = LibraryFactory()
        self.sample.libraries.add(sample_library)

    def test_get_project_file_throw_no_libraries_error(self):
        invalid_download_config = {
            "modality": None,
            "format": None,
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        with self.assertRaises(ValueError):
            ComputedFile.get_project_file(self.project, invalid_download_config)

    def test_get_sample_file_throw_no_libraries_error(self):
        invalid_download_config = {
            "modality": None,
            "format": None,
        }
        with self.assertRaises(ValueError):
            ComputedFile.get_sample_file(self.sample, invalid_download_config)

    def test_get_ccdl_dataset_file(self):
        utils.create_data_dirs()

        ccdl_name = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
        project_id = "SCPCP999990"

        dataset, _ = CCDLDataset.get_or_find_ccdl_dataset(ccdl_name, project_id)
        dataset.save()

        computed_file = ComputedFile.get_dataset_file(dataset)

        # CHECK ZIP FILE
        with ZipFile(dataset.computed_file_local_path) as project_zip:
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.DatasetSingleCellSingleCellExperimentSCPCP999990.COMPUTED_FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        self.assertIsNotNone(computed_file)
        for (
            attribute,
            value,
        ) in (
            test_data.DatasetSingleCellSingleCellExperimentSCPCP999990.COMPUTED_FILE_VALUES.items()
        ):
            msg = f"The actual and expected `{attribute}` values differ in {computed_file}"
            self.assertEqual(getattr(computed_file, attribute), value, msg)

    def test_original_file_zip_namelist(self):
        self.maxDiff = None

        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )
        dataset.save()

        ComputedFile.get_dataset_file(dataset)

        with ZipFile(dataset.computed_file_local_path) as project_zip:
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                sorted(test_data.DatasetCustomSingleCellExperiment.COMPUTED_FILE_LIST),
            )
