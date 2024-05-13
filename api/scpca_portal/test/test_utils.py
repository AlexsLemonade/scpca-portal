import csv
import os
import tempfile
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


class TestWriteDictListToFile(TestCase):
    def setUp(self):
        self.dummy_list_of_dicts = [
            {"country": "USA", "language": "English", "capital": "Washington DC"},
            {"country": "Spain", "language": "Spanish", "capital": "Madrid"},
            {"country": "France", "language": "French", "capital": "Paris"},
            {"country": "Japan", "language": "Japanese", "capital": "Tokyo"},
        ]
        self.dummy_field_names = {"country", "language", "capital"}
        self.dummy_dir = Path(tempfile.mkdtemp())
        self.test_output_file = Path(self.dummy_dir, "test_output.tsv")

    def tearDown(self):
        if Path.exists(self.test_output_file):
            Path.unlink(self.test_output_file)
        if Path.exists(self.dummy_dir):
            Path.rmdir(self.dummy_dir)

    def test_write_dict_list_to_file_successful_write(self):
        delimiter = ","
        utils.write_dict_list_to_file(
            self.dummy_list_of_dicts, self.test_output_file, self.dummy_field_names, delimiter
        )
        self.assertTrue(os.path.exists(self.test_output_file))

    def test_write_dict_list_to_file_read_write_values_match(self):
        delimiter = ","
        utils.write_dict_list_to_file(
            self.dummy_list_of_dicts, self.test_output_file, self.dummy_field_names, delimiter
        )

        with open(self.test_output_file) as output_file:
            output_list_of_dicts = list(csv.DictReader(output_file))
            self.assertEqual(self.dummy_list_of_dicts, output_list_of_dicts)

    def test_write_dict_list_to_file_missing_field_names(self):
        field_names = {"country", "language"}
        delimiter = ","
        with self.assertRaises(ValueError):
            utils.write_dict_list_to_file(
                self.dummy_list_of_dicts, self.test_output_file, field_names, delimiter
            )

    def test_write_dict_list_to_file_invalid_output_file(self):
        invalid_output_file = os.path.join(self.dummy_dir, "invalid", "path", "output.csv")
        delimiter = ","
        with self.assertRaises(FileNotFoundError):
            utils.write_dict_list_to_file(
                self.dummy_list_of_dicts, invalid_output_file, self.dummy_field_names, delimiter
            )
