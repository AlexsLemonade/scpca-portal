from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.models import ComputedFile
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
