from unittest.mock import patch

from django.test import TestCase

from scpca_portal import s3


class TestListBucketObjects(TestCase):
    def setUp(self):
        self.default_bucket = "input-bucket"

    @patch("json.loads")
    @patch("subprocess.run")
    def test_bucket_without_prefix(self, mock_run, _):
        s3.list_bucket_objects(self.default_bucket)

        expected_command_inputs = [
            "aws",
            "s3api",
            "list-objects",
            "--output",
            "json",
            "--bucket",
            self.default_bucket,
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(actual_command_inputs, expected_command_inputs)
        mock_run.assert_called_once()

    @patch("json.loads")
    @patch("subprocess.run")
    def test_bucket_with_prefix(self, mock_run, _):
        prefix = "2025/02/20"
        s3.list_bucket_objects(f"{self.default_bucket}/{prefix}")

        expected_command_inputs = [
            "aws",
            "s3api",
            "list-objects",
            "--output",
            "json",
            "--prefix",
            prefix,
            "--bucket",
            self.default_bucket,
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(actual_command_inputs, expected_command_inputs)
        mock_run.assert_called_once()

    @patch("json.loads")
    @patch("subprocess.run")
    def test_public_in_bucket(self, mock_run, _):
        bucket = "input-bucket-public"
        s3.list_bucket_objects(bucket)

        expected_command_inputs = [
            "aws",
            "s3api",
            "list-objects",
            "--output",
            "json",
            "--bucket",
            bucket,
            "--no-sign-request",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(actual_command_inputs, expected_command_inputs)
        mock_run.assert_called_once()

    @patch("json.loads")
    @patch("subprocess.run")
    def test_mocked_output(self, mock_run, mock_json_loads):
        """
        Test key and value transformations as well as removed directories on mocked output.
        """
        prefix = "2025/02/20"
        mocked_output = {
            "Contents": [
                {"Key": f"{prefix}/dir/", "Size": 0, "ETag": '"d41d8cd98f00b204e9800998ecf8427e"'},
                {
                    "Key": f"{prefix}/dir/file1.html",
                    "Size": 1027847,
                    "ETag": '"a57c42b535f7ed544c6faf6b21a83318"',
                },
                {
                    "Key": f"{prefix}/dir/file2.rds",
                    "Size": 298194872,
                    "ETag": '"18b6f91cc17f5524d1aae7ba8dff6e71-36"',
                },
            ]
        }

        mock_json_loads.return_value = mocked_output
        expected_output = [
            {
                "s3_key": "dir/file1.html",
                "size_in_bytes": 1027847,
                "hash": "a57c42b535f7ed544c6faf6b21a83318",
            },
            {
                "s3_key": "dir/file2.rds",
                "size_in_bytes": 298194872,
                "hash": "18b6f91cc17f5524d1aae7ba8dff6e71",
            },
        ]
        actual_output = s3.list_bucket_objects(f"{self.default_bucket}/{prefix}")

        mock_run.assert_called_once()
        self.assertListEqual(actual_output, expected_output)
