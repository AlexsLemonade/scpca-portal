from django.test import TestCase

from scpca_portal import filter
from scpca_portal.filter import ArrayFieldContainsFilter
from scpca_portal.models import Sample


class FilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SampleFilterSet = filter.build_auto_filterset(
            Sample,
            auto_fields=[
                "scpca_id",  # TextField
                "has_cite_seq_data",  # BooleanField
                "technologies",  # ArrayField
                "sample_cell_count_estimate",  # IntegerField
                "updated_at",  # DateTimeField
            ],
            extra_fields={"project__scpca_id": ["exact"]},
        )

    def test_all_included_fields(self):
        actual_fields = self.SampleFilterSet.base_filters.keys()
        expected_fields = [
            "scpca_id",
            "has_cite_seq_data",
            "technologies",
            "sample_cell_count_estimate",
            "updated_at",
            # extra_fields
            "project__scpca_id",
        ]

        for expected_field in expected_fields:
            self.assertIn(expected_field, actual_fields)

    def test_array_fields(self):
        # Should be an instance of ArrayFieldContainsFilter
        array_field_filter = self.SampleFilterSet.base_filters["technologies"]
        self.assertIsInstance(array_field_filter, ArrayFieldContainsFilter)

    def test_boolean_fields(self):
        # Should support "exact"
        actual_fields = self.SampleFilterSet.base_filters.keys()
        expected_fields = ["has_cite_seq_data"]

        for expected_field in expected_fields:
            self.assertIn(expected_field, actual_fields)

    def test_datetime_fields(self):
        # Should support "exact", "gte", "lte", and "date"
        actual_fields = self.SampleFilterSet.base_filters.keys()
        expected_fields = ["updated_at", "updated_at__gte", "updated_at__lte", "updated_at__date"]

        for expected_field in expected_fields:
            self.assertIn(expected_field, actual_fields)

    def test_integer_fields(self):
        # Should support"exact", "gte", "lte", "gt", "lt", and "in"
        actual_fields = self.SampleFilterSet.base_filters.keys()

        expected_fields = [
            "sample_cell_count_estimate",
            "sample_cell_count_estimate__gte",
            "sample_cell_count_estimate__lte",
            "sample_cell_count_estimate__gt",
            "sample_cell_count_estimate__lt",
            "sample_cell_count_estimate__in",
        ]

        for expected_field in expected_fields:
            self.assertIn(expected_field, actual_fields)

    def test_text_fields(self):
        # Should support "exact", "icontains"
        actual_fields = self.SampleFilterSet.base_filters.keys()
        expected_fields = ["scpca_id", "scpca_id__icontains"]

        for expected_field in expected_fields:
            self.assertIn(expected_field, actual_fields)
