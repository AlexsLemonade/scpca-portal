from django.test import TestCase

from scpca_portal.models import Dataset
from scpca_portal.test.factories import DatasetFactory


class TestDataset(TestCase):
    def test_dataset_saved_to_db(self):
        dataset = DatasetFactory()
        self.assertEqual(Dataset.objects.count(), 1)

        returned_dataset = Dataset.objects.filter(pk=dataset.id).first()
        self.assertEqual(returned_dataset, dataset)
