import csv
import io

from django.test import TestCase

from scpca_portal import common, metadata_file


class TestGetFileContents(TestCase):
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
                "holidays": [
                    "New Year’s Day",
                    "Epiphany",
                    "Christmas Day",
                ],
            },
            {
                "scpca_project_id": "SCPCP999992",
                "scpca_sample_id": "SCPCS999992",
                "scpca_library_id": "SCPCL999992",
                "country": "Antarctica",
                "language": "Antarctic English",
                "holidays": "NA",
            },
            {
                "scpca_project_id": "SCPCP999990",
                "scpca_sample_id": "SCPCS999990",
                "scpca_library_id": "SCPCL999990",
                "country": "USA",
                "language": "English",
                "capital": "Washington DC",
                "holidays": [
                    "New Year's Day",
                    "Thanksgiving Day",
                    "Christmas Day",
                ],
            },
        ]
        self.dummy_field_names = {
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "country",
            "language",
            "capital",
            "holidays",
        }

    def test_get_file_contents_successful_write(self):
        output_file_contents = metadata_file.get_file_contents(
            self.dummy_list_of_dicts, fieldnames=self.dummy_field_names
        )
        self.assertIsNotNone(output_file_contents)
        self.assertIsInstance(output_file_contents, str)

    def test_get_file_contents_read_write_values_match(self):
        expected_output = [
            {
                "scpca_project_id": "SCPCP999990",
                "scpca_sample_id": "SCPCS999990",
                "scpca_library_id": "SCPCL999990",
                "country": "USA",
                "language": "English",
                "capital": "Washington DC",
                "holidays": "New Year's Day;Thanksgiving Day;Christmas Day",
            },
            {
                "scpca_project_id": "SCPCP999991",
                "scpca_sample_id": "SCPCS999991",
                "scpca_library_id": "SCPCL999991",
                "country": "Spain",
                "language": "Spanish",
                "capital": "Madrid",
                "holidays": "New Year’s Day;Epiphany;Christmas Day",
            },
            {
                "scpca_project_id": "SCPCP999992",
                "scpca_sample_id": "SCPCS999992",
                "scpca_library_id": "SCPCL999992",
                "country": "Antarctica",
                "language": "Antarctic English",
                "capital": "NA",
                "holidays": "NA",
            },
        ]

        output_file_contents = metadata_file.get_file_contents(
            self.dummy_list_of_dicts, fieldnames=self.dummy_field_names
        )
        with io.StringIO(output_file_contents) as output_buffer:
            output_list_of_dicts = list(csv.DictReader(output_buffer, delimiter=common.TAB))
            self.assertEqual(expected_output, output_list_of_dicts)

    def test_get_file_contents_read_write_add_missing_field_names(self):
        output_file_contents = metadata_file.get_file_contents(
            self.dummy_list_of_dicts, fieldnames=self.dummy_field_names
        )

        with io.StringIO(output_file_contents) as output_buffer:
            output_list_of_dicts = list(csv.DictReader(output_buffer, delimiter=common.TAB))
            self.assertIn(common.NA, [d["capital"] for d in output_list_of_dicts])

    def test_get_file_contents_incomplete_field_names(self):
        field_names = {"country", "language"}
        with self.assertRaises(ValueError):
            metadata_file.get_file_contents(self.dummy_list_of_dicts, fieldnames=field_names)

    def test_get_file_contents_not_inputted_field_names(self):
        output_file_contents = metadata_file.get_file_contents(self.dummy_list_of_dicts)
        self.assertIsNotNone(output_file_contents)
        self.assertIsInstance(output_file_contents, str)
