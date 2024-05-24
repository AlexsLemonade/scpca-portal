import csv
import os
import tempfile
from pathlib import Path

from django.test import TestCase

from scpca_portal import common, metadata_file


class TestWriteDictsToFile(TestCase):
    def setUp(self):
        self.dummy_list_of_dicts = [
            {"country": "USA", "language": "English", "capital": "Washington DC"},
            {"country": "Spain", "language": "Spanish", "capital": "Madrid"},
            {"country": "France", "language": "French", "capital": "Paris"},
            {"country": "Japan", "language": "Japanese", "capital": "Tokyo"},
        ]
        self.dummy_field_names = {"country", "language", "capital"}
        self.dummy_dir = Path(tempfile.mkdtemp())
        self.dummy_output_path = Path(self.dummy_dir, "dummy_output.tsv")

    def tearDown(self):
        if Path.exists(self.dummy_output_path):
            Path.unlink(self.dummy_output_path)
        if Path.exists(self.dummy_dir):
            Path.rmdir(self.dummy_dir)

    def test_write_dicts_to_file_successful_write(self):
        metadata_file.write_dicts_to_file(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_dicts_to_file_read_write_values_match(self):
        metadata_file.write_dicts_to_file(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )

        with open(self.dummy_output_path) as output_file:
            output_list_of_dicts = list(csv.DictReader(output_file, delimiter=common.TAB))
            self.assertEqual(self.dummy_list_of_dicts, output_list_of_dicts)

    def test_write_dicts_to_file_incomplete_field_names(self):
        field_names = {"country", "language"}
        with self.assertRaises(ValueError):
            metadata_file.write_dicts_to_file(
                self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=field_names
            )

    def test_write_dicts_to_file_not_inputted_field_names(self):
        metadata_file.write_dicts_to_file(self.dummy_list_of_dicts, self.dummy_output_path)
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_dicts_to_file_invalid_output_file(self):
        invalid_output_file = os.path.join(self.dummy_dir, "invalid", "path", "output.csv")
        with self.assertRaises(FileNotFoundError):
            metadata_file.write_dicts_to_file(
                self.dummy_list_of_dicts, invalid_output_file, fieldnames=self.dummy_field_names
            )
