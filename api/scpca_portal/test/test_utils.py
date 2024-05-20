import csv
import os
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import common, utils


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
    @patch("scpca_portal.utils.datetime")
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
        utils.write_dicts_to_file(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_dicts_to_file_read_write_values_match(self):
        utils.write_dicts_to_file(
            self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=self.dummy_field_names
        )

        with open(self.dummy_output_path) as output_file:
            output_list_of_dicts = list(csv.DictReader(output_file, delimiter=common.TAB))
            self.assertEqual(self.dummy_list_of_dicts, output_list_of_dicts)

    def test_write_dicts_to_file_incomplete_field_names(self):
        field_names = {"country", "language"}
        with self.assertRaises(ValueError):
            utils.write_dicts_to_file(
                self.dummy_list_of_dicts, self.dummy_output_path, fieldnames=field_names
            )

    def test_write_dicts_to_file_not_inputted_field_names(self):
        utils.write_dicts_to_file(self.dummy_list_of_dicts, self.dummy_output_path)
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_write_dicts_to_file_invalid_output_file(self):
        invalid_output_file = os.path.join(self.dummy_dir, "invalid", "path", "output.csv")
        with self.assertRaises(FileNotFoundError):
            utils.write_dicts_to_file(
                self.dummy_list_of_dicts, invalid_output_file, fieldnames=self.dummy_field_names
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

        with self.assertRaises(AttributeError):
            utils.get_csv_zipped_values(data, *args)
