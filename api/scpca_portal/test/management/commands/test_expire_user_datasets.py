from datetime import datetime, timedelta
from functools import partial

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.models import UserDataset
from scpca_portal.test.factories import DatasetComputedFileFactory, UserDatasetFactory


class TestExpireUserDatasets(TestCase):
    def setUp(self):
        self.expire_user_datasets = partial(call_command, "expire_user_datasets")
        self.now = make_aware(datetime.now())

    def test_mark_expired_dataset(self):
        # Set up 3 expired datasets
        datasets = [
            UserDatasetFactory(
                expires_at=self.now - timedelta(days=8) + timedelta(days=7),
                is_expired=False,
                is_succeeded=True,
                succeeded_at=self.now - timedelta(days=8),
                computed_file=DatasetComputedFileFactory(),
            )
            for _ in range(3)
        ]

        self.expire_user_datasets()
        # Should mark the dataset as expired and purge computed files
        for dataset in datasets:
            updated_dataset = UserDataset.objects.get(id=dataset.id)
            self.assertTrue(updated_dataset.is_expired)
            self.assertIsNone(updated_dataset.computed_file)

    def test_mark_no_expired_dataset(self):
        # Set up 3 unexpired datasets
        datasets = [
            UserDatasetFactory(
                expires_at=self.now + timedelta(days=7),
                is_expired=False,
                is_succeeded=True,
                succeeded_at=self.now,
                computed_file=DatasetComputedFileFactory(),
            )
            for _ in range(3)
        ]

        self.expire_user_datasets()
        # Should not mark the dataset as expired or purge computed files
        for dataset in datasets:
            updated_dataset = UserDataset.objects.get(id=dataset.id)
            self.assertFalse(updated_dataset.is_expired)
            self.assertIsNotNone(updated_dataset.computed_file)
