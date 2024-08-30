import csv
import io
from typing import Dict, List

from django.test import TestCase

from scpca_portal import common, metadata_file
from scpca_portal.test.factories import LibraryFactory, SampleFactory


class TestGetFileContents(TestCase):
    def setUp(self):
        self.libraries = [LibraryFactory() for _ in range(3)]
        for library in self.libraries:
            library.samples.add(SampleFactory(project=library.project))

        # Allow quick access to one library for easy modification
        self.first_library = self.libraries[0]

        # Pre-compute value for easy reference (not all tests use this value)
        self.libraries_metadata = self.get_libraries_metadata(self.libraries)

    def get_libraries_metadata(self, libraries: List) -> List[Dict]:
        """Lazy compute libraries_metadata value if libraries are mutated."""
        return [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]

    def test_get_file_contents_successful_write(self):
        output_file_contents = metadata_file.get_file_contents(self.libraries_metadata)
        self.assertIsNotNone(output_file_contents)
        self.assertIsInstance(output_file_contents, str)

    def test_get_file_contents_read_write_values_match(self):
        output_file_contents = metadata_file.get_file_contents(self.libraries_metadata)
        with io.StringIO(output_file_contents) as output_buffer:
            output_list_of_dicts = list(csv.DictReader(output_buffer, delimiter=common.TAB))
            for output_dict in output_list_of_dicts:
                id = "scpca_library_id"
                input_dict = next(lm for lm in self.libraries_metadata if lm[id] == output_dict[id])
                # Cast all values in input_dict to str to match str types of string buffer
                formatted_input_dict = {k: str(v) for k, v in input_dict.items()}
                self.assertEqual(output_dict, formatted_input_dict)

    def test_get_file_contents_multi_value_field(self):
        self.first_library.metadata["technology"] = ["first", "second", "third"]
        libraries_metadata = self.get_libraries_metadata(self.libraries)
        output_file_contents = metadata_file.get_file_contents(libraries_metadata)

        with io.StringIO(output_file_contents) as output_buffer:
            first_output_dict = next(csv.DictReader(output_buffer, delimiter=common.TAB))
            self.assertEqual(first_output_dict["technology"], "first;second;third")

    def test_get_file_contents_missing_field_name(self):
        self.first_library.metadata.pop("workflow_version")
        libraries_metadata = self.get_libraries_metadata(self.libraries)
        output_file_contents = metadata_file.get_file_contents(libraries_metadata)

        with io.StringIO(output_file_contents) as output_buffer:
            first_output_dict = next(csv.DictReader(output_buffer, delimiter=common.TAB))
            self.assertEqual(first_output_dict["workflow_version"], "NA")

    def test_get_file_contents_test_sort_order(self):
        libraries_reversed = list(reversed(self.libraries))
        libraries_metadata = self.get_libraries_metadata(libraries_reversed)
        output_file_contents = metadata_file.get_file_contents(libraries_metadata)

        with io.StringIO(output_file_contents) as output_buffer:
            output_list_of_dicts = list(csv.DictReader(output_buffer, delimiter=common.TAB))
            for library, output_dict in zip(self.libraries, output_list_of_dicts):
                self.assertEqual(library.scpca_id, output_dict["scpca_library_id"])
