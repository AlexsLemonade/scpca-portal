import csv
import os
import tempfile
from pathlib import Path

from django.test import TestCase

from scpca_portal import common, metadata_file


class TestWriteMetadataDicts(TestCase):
    def setUp(self):
        self.dummy_list_of_dicts = [
            # This list is intentionally out of order to test the sorting.
            {
                "scpca_project_id": "SCPCP999991",
                "scpca_sample_id": "SCPCS999991",
                "scpca_library_id": "SCPCL999991",
                "country": "Spain",
                "language": "Spanish",
                "capital": "Madrid",
            },
            {
                "scpca_project_id": "SCPCP999994",
                "scpca_sample_id": "SCPCS999994",
                "scpca_library_id": "SCPCL999994",
                "country": "Antarctica",
                "language": "Antarctic English",
            },
            {
                "scpca_project_id": "SCPCP999990",
                "scpca_sample_id": "SCPCS999990",
                "scpca_library_id": "SCPCL999990",
                "country": "USA",
                "language": "English",
                "capital": "Washington DC",
            },
        ]
        self.dummy_field_names = {
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "country",
            "language",
            "capital",
        }
        self.dummy_dir = Path(tempfile.mkdtemp())
        self.dummy_output_path = Path(self.dummy_dir, "dummy_output.tsv")

    def tearDown(self):
        if Path.exists(self.dummy_output_path):
            Path.unlink(self.dummy_output_path)
        if Path.exists(self.dummy_dir):
            Path.rmdir(self.dummy_dir)

    def test_write_metadata_dicts_successful_write(self):
        metadata_file.write_metadata_dicts(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_metadata_dicts_read_write_values_match(self):
        expected_output = [
            {
                "scpca_project_id": "SCPCP999990",
                "scpca_sample_id": "SCPCS999990",
                "scpca_library_id": "SCPCL999990",
                "country": "USA",
                "language": "English",
                "capital": "Washington DC",
            },
            {
                "scpca_project_id": "SCPCP999991",
                "scpca_sample_id": "SCPCS999991",
                "scpca_library_id": "SCPCL999991",
                "country": "Spain",
                "language": "Spanish",
                "capital": "Madrid",
            },
            {
                "scpca_project_id": "SCPCP999994",
                "scpca_sample_id": "SCPCS999994",
                "scpca_library_id": "SCPCL999994",
                "country": "Antarctica",
                "language": "Antarctic English",
                "capital": "NA",
            },
        ]

        metadata_file.write_metadata_dicts(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )

        with open(self.dummy_output_path) as output_file:
            output_list_of_dicts = list(csv.DictReader(output_file, delimiter=common.TAB))
            self.assertEqual(expected_output, output_list_of_dicts)

    def test_write_metadata_dicts_read_write_add_missing_field_names(self):
        metadata_file.write_metadata_dicts(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )

        with open(self.dummy_output_path) as output_file:
            output_list_of_dicts = list(csv.DictReader(output_file, delimiter=common.TAB))
            self.assertIn(common.NA, [d["capital"] for d in output_list_of_dicts])

    def test_write_metadata_dicts_incomplete_field_names(self):
        field_names = {"country", "language"}
        with self.assertRaises(ValueError):
            metadata_file.write_metadata_dicts(
                self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=field_names
            )

    def test_write_metadata_dicts_not_inputted_field_names(self):
        metadata_file.write_metadata_dicts(self.dummy_list_of_dicts, self.dummy_output_path)
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_metadata_dicts_invalid_output_file(self):
        invalid_output_file = os.path.join(self.dummy_dir, "invalid", "path", "output.csv")
        with self.assertRaises(FileNotFoundError):
            metadata_file.write_metadata_dicts(
                self.dummy_list_of_dicts, invalid_output_file, fieldnames=self.dummy_field_names
            )
