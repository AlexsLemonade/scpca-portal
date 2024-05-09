from datetime import date
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
