from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag

from scpca_portal import s3


class TestS3(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    def setUp(self):
        self.default_bucket = "input-bucket"

    @tag("list_bucket_objects")
    @patch("json.loads")
    @patch("subprocess.run")
    def test_list_bucket_without_prefix(self, mock_run, _):
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

    @tag("list_bucket_objects")
    @patch("json.loads")
    @patch("subprocess.run")
    def test_list_bucket_with_prefix(self, mock_run, _):
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

    @tag("list_bucket_objects")
    @patch("json.loads")
    @patch("subprocess.run")
    def test_list_public_in_bucket(self, mock_run, _):
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

    @tag("list_bucket_objects")
    @patch("json.loads")
    @patch("subprocess.run")
    def test_list_mocked_output(self, mock_run, mock_json_loads):
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

    @tag("list_bucket_objects")
    def test_list_test_inputs(self):
        bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        actual_objects = s3.list_bucket_objects(bucket)

        # assert total number of files
        TOTAL_OBJECTS = 99
        TOTAL_DIRECTORIES = 17
        TOTAL_FILES = TOTAL_OBJECTS - TOTAL_DIRECTORIES
        self.assertEqual(len(actual_objects), TOTAL_FILES)

        # assert correct key transformations
        key_set = {key for obj in actual_objects for key in obj.keys()}
        # assert key transform "Key" -> "s3_key"
        self.assertNotIn("Key", key_set)
        self.assertIn("s3_key", key_set)
        # assert key transform "Size" -> "size_in_bytes"
        self.assertNotIn("Size", key_set)
        self.assertIn("size_in_bytes", key_set)
        # assert key transform "ETag" -> "hash"
        self.assertNotIn("ETag", key_set)
        self.assertIn("hash", key_set)

        # assert hash value transformation
        hashes = set(obj["hash"] for obj in actual_objects)
        self.assertFalse(any(True for hash_value in hashes if '"' in hash_value))
        self.assertFalse(any(True for hash_value in hashes if "-" in hash_value))

        # assert s3_key value transformation
        # the test bucket is a combination of a bucket name and a directory
        # which must be extracted in order to make sure that s3_key transformation works correctly
        s3_key_prefix = bucket.split("/", 1)[1]
        s3_keys = set(obj["s3_key"] for obj in actual_objects)
        self.assertFalse(any(True for s3_key in s3_keys if s3_key.startswith(s3_key_prefix)))

        # assert no dirs
        self.assertFalse(any(True for obj in actual_objects if obj["s3_key"].endswith("/")))
