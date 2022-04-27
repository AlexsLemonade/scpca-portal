from django.test import TestCase

from scpca_portal import utils


class TestUtils(TestCase):
    def test_boolean_from_string_raises_exception(self):
        for v in (-1, 1.2, None):
            with self.assertRaises(ValueError) as ctx:
                utils.boolean_from_string(v)

    def test_boolean_from_string_returns_false(self):
        for v in (False, "False", "false", "ANY", "Other", "string"):
            self.assertFalse(utils.boolean_from_string(v))

    def test_boolean_from_string_true(self):
        for v in (True, "True", "TRUE", "t", "tRUe"):
            self.assertTrue(utils.boolean_from_string(v))
