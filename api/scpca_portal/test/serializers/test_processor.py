from django.forms.models import model_to_dict
from django.test import TestCase

from scpca_portal.test.factories import ProcessorFactory
from scpca_portal.views.processor import ProcessorDetailSerializer, ProcessorSerializer


class TestProcessorSerializer(TestCase):
    def setUp(self):
        self.processor_data = model_to_dict(ProcessorFactory())

    def test_serializer_with_empty_data(self):
        serializer = ProcessorSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_detail_serializer_with_empty_data(self):
        serializer = ProcessorDetailSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_serializer_with_valid_data(self):
        serializer = ProcessorSerializer(data=self.processor_data)
        self.assertTrue(serializer.is_valid())

    def test_detail_serializer_with_valid_data(self):
        serializer = ProcessorDetailSerializer(data=self.processor_data)
        self.assertTrue(serializer.is_valid())
