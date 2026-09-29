"""Tests for how ScPCA's "no value" markers become CCDI nulls."""

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi.mapping import reported
from scpca_portal.test.federation.ccdi.mapping.helpers import build_sample


class ReportedTests(SimpleTestCase):
    def test_a_submitted_value_survives(self):
        self.assertEqual(reported("Glioblastoma"), "Glioblastoma")

    def test_scpca_placeholders_read_as_absent(self):
        for placeholder in ("NA", "", "   "):
            with self.subTest(value=placeholder):
                self.assertIsNone(reported(placeholder))

    def test_values_are_stripped(self):
        self.assertEqual(reported("  1463 "), "1463")

    def test_a_missing_value_reads_as_absent(self):
        self.assertIsNone(reported(None))

    def test_placeholders_are_matched_exactly(self):
        # `unknown` is a real age_timing value, not a marker of absence, so the
        # match stays case-sensitive and narrow.
        for value in ("unknown", "Unknown"):
            with self.subTest(value=value):
                self.assertEqual(reported(value), value)

    def test_non_strings_pass_through(self):
        # Zero is a value, not an absence.
        self.assertEqual(reported(0), 0)
        self.assertEqual(reported(False), False)

    def test_it_reads_from_either_store(self):
        # ScPCA keeps metadata both in the JSON and on columns, and neither is
        # normalised on the way in.
        sample = build_sample(diagnosis="NA")
        sample.subdiagnosis = "NA"

        self.assertIsNone(reported(sample.metadata.get("diagnosis")))
        self.assertIsNone(reported(sample.subdiagnosis))
