import subprocess
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import s3


class TestListInputPaths(TestCase):
    def setUp(self):
        self.default_bucket_name = "input-bucket"
        self.default_relative_path = Path("relative-path/")

    @patch("subprocess.run")
    def test_list_input_paths_correct_command_inputs(self, mock_run):
        s3.list_input_paths(self.default_relative_path, self.default_bucket_name, recursive=False)
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{self.default_bucket_name}/{self.default_relative_path}/",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_list_input_paths_recursive_flag_passed_by_default(self, mock_run):
        s3.list_input_paths(self.default_relative_path, self.default_bucket_name)
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{self.default_bucket_name}/{self.default_relative_path}/",
            # No need to pass recursive=True to function call as this is default behavior
            "--recursive",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_list_input_paths_public_in_bucket_name(self, mock_run):
        public_bucket_name = "public-input-bucket"
        s3.list_input_paths(self.default_relative_path, public_bucket_name, recursive=False)
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{public_bucket_name}/{self.default_relative_path}/",
            "--no-sign-request",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_list_input_paths_command_success_recursive(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[
                "aws",
                "s3",
                "ls",
                f"s3://{self.default_bucket_name}/{self.default_relative_path}/",
            ],
            returncode=0,
            stdout=f"2024-06-10 10:00:00 1234 {self.default_relative_path}/file1.txt\n"
            f"2024-06-10 10:00:00 1234 {self.default_relative_path}/file2.txt",
        )
        result = s3.list_input_paths(
            self.default_relative_path, self.default_bucket_name, recursive=True
        )
        expected = [
            self.default_relative_path / "file1.txt",
            self.default_relative_path / "file2.txt",
        ]
        self.assertEqual(result, expected)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_list_input_paths_command_success_non_recursive(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[
                "aws",
                "s3",
                "ls",
                # Without a '/' at the end of the s3 resource location,
                # dir contents will not be listed,
                # but rather an entry of the relative path itself
                f"s3://{self.default_bucket_name}/{self.default_relative_path}/",
            ],
            returncode=0,
            stdout="PRE dir1/\nPRE dir2/",
        )
        expected = [Path("dir1/"), Path("dir2/")]
        result = s3.list_input_paths(self.default_relative_path, self.default_bucket_name)
        self.assertEqual(expected, result)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_list_input_paths_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=f"aws s3 ls s3://{self.default_bucket_name}/{self.default_relative_path}/",
        )
        result = s3.list_input_paths(self.default_relative_path, self.default_bucket_name)
        expected = []
        self.assertEqual(result, expected)
        mock_run.assert_called_once()
