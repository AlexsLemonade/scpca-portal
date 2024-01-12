from django.forms.models import model_to_dict
from django.test import TestCase

from scpca_portal.test.factories import SampleComputedFileFactory
from scpca_portal.views.computed_file import ComputedFileDetailSerializer, ComputedFileSerializer


class TestComputedFileSerializer(TestCase):
    def setUp(self):
        self.computed_file_data = model_to_dict(SampleComputedFileFactory())

    def assertContainsFields(self, serializer):
        for field in ("format", "modality", "type"):
            self.assertIn(field, serializer.data)

    def test_serializer_with_empty_data(self):
        serializer = ComputedFileSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_detail_serializer_with_empty_data(self):
        serializer = ComputedFileDetailSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_serializer_with_valid_data(self):
        serializer = ComputedFileSerializer(data=self.computed_file_data)
        self.assertTrue(serializer.is_valid())
        self.assertContainsFields(serializer)

    def test_detail_serializer_with_valid_data(self):
        serializer = ComputedFileDetailSerializer(data=self.computed_file_data)
        self.assertTrue(serializer.is_valid())
        self.assertContainsFields(serializer)
