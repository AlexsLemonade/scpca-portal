from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal.models import ComputedFile


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
