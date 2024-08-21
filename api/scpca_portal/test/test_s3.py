import subprocess
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import s3


class TestListInputPaths(TestCase):
    @patch("subprocess.run")
    def test_list_input_paths_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", "s3://input-bucket"],
            returncode=0,
            stdout="2024-06-10 10:00:00 1234 file.txt\nPRE dir/",
        )
        result = s3.list_input_paths(bucket_path=Path("input-bucket"))
        expected = [Path("file.txt"), Path("dir/")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="aws s3 ls s3://input-bucket"
        )
        result = s3.list_input_paths(bucket_path=Path("input-bucket"))
        expected = []
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_with_relative_path(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", "s3://input-bucket/relative/path"],
            returncode=0,
            stdout="2024-06-10 10:00:00 1234 file.txt\nPRE dir/",
        )
        result = s3.list_input_paths(
            relative_path=Path("relative/path"), bucket_path=Path("input-bucket")
        )
        expected = [Path("file.txt"), Path("dir/")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_with_public_bucket(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", "s3://public-input-bucket", "--no-sign-request"],
            returncode=0,
            stdout="2024-06-10 10:00:00 1234 file.txt\nPRE dir/",
        )
        result = s3.list_input_paths(bucket_path=Path("public-input-bucket"))
        expected = [Path("file.txt"), Path("dir/")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_list_input_paths_with_nested_directory(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", "s3://input-bucket/nested-dir"],
            returncode=0,
            stdout="2024-06-10 10:00:00 1234 nested-dir/file.txt\nPRE nested-dir/dir/",
        )
        expected = [Path("nested-dir/file.txt"), Path("nested-dir/dir/")]
        result = s3.list_input_paths(bucket_path=Path("input-bucket"))
        self.assertEqual(expected, result)

    @patch("subprocess.run")
    def test_list_input_paths_non_recursive_path(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["aws", "s3", "ls", "s3://input-bucket/nested-dir"],
            returncode=0,
            stdout="PRE nested-dir",
        )
        expected = [Path("nested-dir")]
        result = s3.list_input_paths(
            bucket_path=Path("input-bucket"), relative_path=Path("nested-dir"), recursive=False
        )
        self.assertEqual(expected, result)
