import subprocess
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from scpca_portal import s3


class TestListInputPaths(TestCase):
    def setUp(self):
        self.input_bucket_name = settings.AWS_S3_INPUT_BUCKET_NAME
        self.nested_input_bucket_dirs = self.get_nested_input_bucket_dirs(self.input_bucket_name)
        self.empty_relative_path = Path()
        self.default_bucket_name = "input-bucket"
        self.default_relative_path = Path("relative-path")

    def get_nested_input_bucket_dirs(self, bucket_name: str) -> str:
        if nested_input_bucket_path_parts := bucket_name.split("/")[1:]:
            return "/".join(nested_input_bucket_path_parts)

        return ""

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
    def test_list_input_paths_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", f"s3://{self.input_bucket_name}"],
            returncode=0,
            stdout=f"2024-06-10 10:00:00 1234 {self.nested_input_bucket_dirs}/file.txt\n"
            f"PRE {self.nested_input_bucket_dirs}/dir/",
        )
        result = s3.list_input_paths(self.empty_relative_path, self.input_bucket_name)
        expected = [Path("file.txt"), Path("dir/")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=f"aws s3 ls s3://{self.input_bucket_name}"
        )
        result = s3.list_input_paths(self.empty_relative_path, self.input_bucket_name)
        expected = []
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_with_relative_path(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", f"s3://{self.input_bucket_name}/relative/path"],
            returncode=0,
            stdout=f"2024-06-10 10:00:00 1234 {self.nested_input_bucket_dirs}/file.txt\n"
            f"PRE {self.nested_input_bucket_dirs}/dir/",
        )
        result = s3.list_input_paths(Path("relative/path"), self.input_bucket_name)
        expected = [Path("file.txt"), Path("dir/")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_with_nested_directory(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", f"s3://{self.input_bucket_name}/nested-dir"],
            returncode=0,
            stdout=f"2024-06-10 10:00:00 1234 {self.nested_input_bucket_dirs}/nested-dir/file.txt\n"
            f"PRE {self.nested_input_bucket_dirs}/nested-dir/dir/",
        )
        expected = [Path("nested-dir/file.txt"), Path("nested-dir/dir/")]
        result = s3.list_input_paths(Path("nested-dir"), self.input_bucket_name)
        self.assertEqual(expected, result)

    @patch("subprocess.run")
    def test_list_input_paths_non_recursive_path(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", f"s3://{self.input_bucket_name}/nested-dir"],
            returncode=0,
            stdout="PRE nested-dir",
        )
        expected = [Path("nested-dir")]
        result = s3.list_input_paths(Path("nested-dir"), self.input_bucket_name, recursive=False)
        self.assertEqual(expected, result)
