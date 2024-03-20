from django.forms.models import model_to_dict
from django.test import TestCase

from scpca_portal.test.factories import SampleFactory
from scpca_portal.views.sample import SampleDetailSerializer, SampleSerializer


class TestSampleSerializer(TestCase):
    def setUp(self):
        self.sample_data = model_to_dict(SampleFactory())
        # This needs to be unique.
        self.sample_data["scpca_id"] = "SCPCS999999"

    def test_serializer_with_empty_data(self):
        serializer = SampleSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_detail_serializer_with_empty_data(self):
        serializer = SampleDetailSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_serializer_with_valid_data(self):
        serializer = SampleSerializer(data=self.sample_data)
        self.assertTrue(serializer.is_valid())

    def test_detail_serializer_with_valid_data(self):
        serializer = SampleDetailSerializer(data=self.sample_data)
        self.assertTrue(serializer.is_valid())

    def test_existence_of_is_cell_line_and_is_xenograft_properties(self):
        serializer = SampleSerializer(data=self.sample_data)
        self.assertTrue('is_cell_line' in serializer.fields.keys())
        self.assertTrue('is_xenograft' in serializer.fields.keys())
