from datetime import date
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import utils


class TestBooleanFromString(TestCase):
    def test_raise_exception(self):
        for v in (-1, 1.2, None):
            with self.assertRaises(ValueError):
                utils.boolean_from_string(v)

    def test_return_false(self):
        for v in (False, "False", "false", "ANY", "Other", "string"):
            self.assertFalse(utils.boolean_from_string(v))

    def test_return_true(self):
        for v in (True, "True", "TRUE", "t", "tRUe"):
            self.assertTrue(utils.boolean_from_string(v))


class TestStringFromList(TestCase):
    def test_return_joined_string(self):
        list = ["a", "b", "c"]
        expected_result = "a;b;c"
        actual_result = utils.string_from_list(list)

        self.assertEqual(actual_result, expected_result)

    def test_ignores_nonlist(self):
        items = ["abc", 123, None, {"a": 1, "b": 2, "c": 3}]
        actual_result = [utils.string_from_list(item) for item in items]

        self.assertEqual(actual_result, items)


class TestJoinWorkflowVersions(TestCase):
    def test_join_duplicate_values(self):
        items = ("an item", "an item", "another item")
        self.assertEqual(utils.join_workflow_versions(items), "an item, another item")

    def test_join_empty_value(self):
        self.assertEqual(utils.join_workflow_versions([]), "")

    def test_join_multiple_items(self):
        test_pairs = (
            (("v10", "v1", "v1.0", "v10.1.1"), "v1, v1.0, v10, v10.1.1"),
            (("v1", "v2", "v3", "v2.1", "v2.1.2"), "v1, v2, v2.1, v2.1.2, v3"),
        )
        for value, result in test_pairs:
            self.assertEqual(utils.join_workflow_versions(value), result)

    def test_join_single_item(self):
        items = ("single item",)
        self.assertEqual(utils.join_workflow_versions(items), items[0])


class TestGetToday(TestCase):
    @patch("scpca_portal.utils.helpers.datetime")
    def test_format(self, mock_date):
        mock_date.today.return_value = date(2022, 10, 8)
        self.assertEqual(utils.get_today_string(), "2022-10-08")


class TestFilterDictListByKeys(TestCase):
    def test_included_keys_exist(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        included_keys = ["a", "b"]

        expected_result = [{"a": 1, "b": 2}, {"a": 4, "b": 5}]
        actual_result = utils.filter_dict_list_by_keys(list_of_dicts, included_keys)

        self.assertEqual(actual_result, expected_result)

    def test_included_keys_do_not_exist(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        included_keys = ["x", "y"]

        with self.assertRaises(ValueError):
            utils.filter_dict_list_by_keys(list_of_dicts, included_keys, ignore_value_error=False)

    def test_included_keys_not_subset(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        included_keys = ["a", "b", "x"]

        with self.assertRaises(ValueError):
            utils.filter_dict_list_by_keys(list_of_dicts, included_keys, ignore_value_error=False)

    def test_included_keys_do_not_exist_ignore_value_error(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        included_keys = ["x", "y"]

        expected_result = [{}, {}]
        actual_result = utils.filter_dict_list_by_keys(
            list_of_dicts, included_keys, ignore_value_error=True
        )

        self.assertEqual(actual_result, expected_result)

    def test_included_keys_not_subset_ignore_value_error(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        included_keys = ["a", "b", "x"]

        expected_result = [{"a": 1, "b": 2}, {"a": 4, "b": 5}]
        actual_result = utils.filter_dict_list_by_keys(
            list_of_dicts, included_keys, ignore_value_error=True
        )

        self.assertEqual(actual_result, expected_result)


class TestGetKeysFromDicts(TestCase):
    def test_get_keys_from_dicts_same_keys(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"c": 4, "b": 5, "a": 6}]
        expected_superset = {"a", "b", "c"}
        self.assertEqual(utils.get_keys_from_dicts(list_of_dicts), expected_superset)

    def test_get_key_s_from_dicts_different_keys(self):
        list_of_dicts = [{"a": 1, "b": 2, "c": 3}, {"c": 4, "d": 5, "e": 6}]
        expected_superset = {"a", "b", "c", "d", "e"}
        self.assertEqual(utils.get_keys_from_dicts(list_of_dicts), expected_superset)


class TestGetSortedFieldNames(TestCase):
    def test_get_sorted_field_names_from_set_of_keys(self):
        list_of_dicts = [
            {
                "scpca_project_id": "SCPCP999990",
                "organism": "Homo sapiens",
                "subdiagnosis": "NA",
                "diagnosis": "diagnosis1",
                "tissue_ontology_term_id": "NA",
                "location_class": "NA",
            },
            {
                "organism": "Homo sapiens",
                "technology": "techonology1",
                "submitter_id": "NA",
                "scpca_sample_id": "SCPCS000490",
                "WHO_grade": "1",
                "organism_ontology_id": "NA",
            },
        ]
        expected_result = [
            "scpca_project_id",
            "scpca_sample_id",
            "diagnosis",
            "subdiagnosis",
            "submitter_id",
            "organism",
            "organism_ontology_id",
            "tissue_ontology_term_id",
            "location_class",
            "WHO_grade",
            "technology",
        ]

        self.assertEqual(
            utils.get_sorted_field_names(utils.get_keys_from_dicts(list_of_dicts)), expected_result
        )


class TestGetCsvZippedValues(TestCase):
    def test_get_csv_zipped_values_same_length_values(self):
        data = {
            "country": "USA;Spain;France;Japan",
            "language": "English;Spanish;French;Japanese",
            "capital": "Washington DC;Madrid;Paris;Tokyo",
        }
        args = ["country", "language", "capital"]

        expected_result = [
            ("USA", "English", "Washington DC"),
            ("Spain", "Spanish", "Madrid"),
            ("France", "French", "Paris"),
            ("Japan", "Japanese", "Tokyo"),
        ]
        actual_result = utils.get_csv_zipped_values(data, *args)

        self.assertEqual(expected_result, actual_result)

    def test_get_csv_zipped_value_different_length_values(self):
        data = {
            "country": "USA;Spain;France;Japan",
            "language": "English;Spanish;French;Japanese",
            "capital": "Washington DC;Madrid",
        }
        args = ["country", "language", "capital"]

        with self.assertRaises(ValueError):
            utils.get_csv_zipped_values(data, *args)

    def test_get_csv_zipped_values_keys_not_present(self):
        data = {
            "country": "USA;Spain;France;Japan",
            "language": "English;Spanish;French;Japanese",
            "capital": "Washington DC;Madrid;Paris;Tokyo",
        }
        args = ["country", "language", "population", "currency"]

        with self.assertRaises(ValueError):
            utils.get_csv_zipped_values(data, *args)


class TestPathReplace(TestCase):
    def test_single_occurrence(self):
        old_extension = ".jpg"
        new_extension = ".png"

        old_path = Path("root/dir/subdir/image.jpg")
        new_path = utils.path_replace(old_path, old_extension, new_extension)

        self.assertEqual(new_path.suffix, new_extension)
        self.assertNotEqual(old_path.suffix, new_path.suffix)

        for old_path_part, new_path_part in zip(old_path.parts, new_path.parts):
            if old_path_part == old_path.name:
                continue
            self.assertEqual(old_path_part, new_path_part)

    def test_multiple_occurences(self):
        old_value = "dir"
        new_value = "folder"

        old_path = Path("rootdir/dir/subdir/image.jpg")
        new_path = utils.path_replace(old_path, old_value, new_value)

        for old_path_part, new_path_part in zip(old_path.parts, new_path.parts):
            if old_value in old_path_part:
                self.assertIn(new_value, new_path_part)

        expected_folder_count = 3
        actual_folder_count = str(new_path).count(new_value)
        self.assertEqual(actual_folder_count, expected_folder_count)


class TestByteConversion(TestCase):
    def test_format_bytes(self):
        # assert gb formatted correctly
        size_in_bytes = 1234567890
        self.assertEqual(utils.format_bytes(size_in_bytes), "1.15 GB")

        # assert mb formatted correctly
        size_in_bytes = 12345678
        self.assertEqual(utils.format_bytes(size_in_bytes), "11.77 MB")

        # assert kb formatted correctly
        size_in_bytes = 123456
        self.assertEqual(utils.format_bytes(size_in_bytes), "120.56 KB")

        # assert bytes formatted correctly
        size_in_bytes = 123
        self.assertEqual(utils.format_bytes(size_in_bytes), "123 Bytes")

        # assert invalid size_in_bytes throws exception
        size_in_bytes = -10
        with self.assertRaises(ValueError):
            utils.format_bytes(size_in_bytes)


class TestHashValues(TestCase):
    def test_hash_values(self):
        values = ["apple", "orange", "banana"]
        self.assertEqual(utils.hash_values(values), "efbcafb6aa8af004895ba045078f2fa2")

        values = ["banana", "apple", "orange"]
        self.assertEqual(utils.hash_values(values), "efbcafb6aa8af004895ba045078f2fa2")
