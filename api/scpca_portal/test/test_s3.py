import subprocess
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import s3


class TestListInputPaths(TestCase):
    def setUp(self):
        self.default_bucket_name = "input-bucket"
        self.default_relative_path = Path("relative-path")

    @patch("subprocess.run")
    def test_list_input_paths_correct_command_inputs(self, mock_run):
        s3.list_input_paths(self.default_relative_path, self.default_bucket_name, recursive=False)
        mock_run.assert_called_once()
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{self.default_bucket_name}/{self.default_relative_path}",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)

    @patch("subprocess.run")
    def test_list_input_paths_recursive_flag_passed(self, mock_run):
        s3.list_input_paths(self.default_relative_path, self.default_bucket_name, recursive=True)
        mock_run.assert_called_once()
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{self.default_bucket_name}/{self.default_relative_path}",
            "--recursive",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)

    @patch("subprocess.run")
    def test_list_input_paths_public_in_bucket_name(self, mock_run):
        public_bucket_name = "public-input-bucket"
        s3.list_input_paths(self.default_relative_path, public_bucket_name, recursive=False)
        mock_run.assert_called_once()
        expected_command_inputs = [
            "aws",
            "s3",
            "ls",
            f"s3://{public_bucket_name}/{self.default_relative_path}",
            "--no-sign-request",
        ]
        actual_command_inputs = mock_run.call_args.args[0]
        self.assertEqual(expected_command_inputs, actual_command_inputs)

    @patch("subprocess.run")
    def test_list_input_paths_command_success_recursive(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[
                "aws",
                "s3",
                "ls",
                f"s3://{self.default_bucket_name}/{self.default_relative_path}",
            ],
            returncode=0,
            stdout=f"2024-06-10 10:00:00 1234 {self.default_relative_path}/file.txt\n"
            f"PRE {self.default_relative_path}/dir/",
        )
        # recursive=True is not passed to test that the default value is recursive=True
        result = s3.list_input_paths(self.default_relative_path, self.default_bucket_name)
        expected = [self.default_relative_path / "file.txt", self.default_relative_path / "dir/"]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_command_success_non_recursive(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[
                "aws",
                "s3",
                "ls",
                f"s3://{self.default_bucket_name}/{self.default_relative_path}",
            ],
            returncode=0,
            stdout=f"PRE {self.default_relative_path}",
        )
        expected = [self.default_relative_path]
        result = s3.list_input_paths(
            self.default_relative_path, self.default_bucket_name, recursive=False
        )
        self.assertEqual(expected, result)

    @patch("subprocess.run")
    def test_list_input_paths_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=f"aws s3 ls s3://{self.default_bucket_name}/{self.default_relative_path}",
        )
        result = s3.list_input_paths(self.default_relative_path, self.default_bucket_name)
        expected = []
        self.assertEqual(result, expected)
