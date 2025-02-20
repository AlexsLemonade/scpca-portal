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
    def test_directories_correctly_excluded(self, mock_run, mock_json_loads):
        s3_output = {
            "Contents": [
                {"Key": "dir/", "Size": 123, "ETag": "ABC"},
                {"Key": "dir/file1.txt", "Size": 456, "ETag": "DEF"},
                {"Key": "dir/file2.txt", "Size": 789, "ETag": "GHI"},
            ]
        }

        mock_json_loads.return_value = s3_output
        expected_output = [
            {"s3_key": "dir/file1.txt", "size_in_bytes": 456, "hash": "DEF"},
            {"s3_key": "dir/file2.txt", "size_in_bytes": 789, "hash": "GHI"},
        ]
        actual_output = s3.list_bucket_objects(self.default_bucket)

        mock_run.assert_called_once()
        self.assertListEqual(actual_output, expected_output)
