from django.test import TestCase

from scpca_portal.enums import FileFormatsTest
from scpca_portal.models import Dataset


class TestDataset(TestCase):
    def setUp(self):
        self.dataset = Dataset.objects.create(format=FileFormatsTest.SINGLE_CELL_EXPERIMENT.name)

    def test_query_by_enum_name(self):
        queried_dataset = Dataset.objects.get(format=FileFormatsTest.SINGLE_CELL_EXPERIMENT.name)
        self.assertEqual(queried_dataset.format, FileFormatsTest.SINGLE_CELL_EXPERIMENT.name)
