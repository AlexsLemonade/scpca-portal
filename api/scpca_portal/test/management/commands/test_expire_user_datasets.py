from datetime import datetime, timedelta
from functools import partial

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import DatasetStates
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
                state=DatasetStates.SUCCEEDED,
                computed_file=DatasetComputedFileFactory(),
            )
            for _ in range(3)
        ]

        self.expire_user_datasets()
        # Should mark the dataset as expired and delete computed files in the database
        for dataset in datasets:
            updated_dataset = UserDataset.objects.get(id=dataset.id)
            self.assertEqual(updated_dataset.state, DatasetStates.EXPIRED)
            self.assertIsNone(updated_dataset.computed_file)

    def test_mark_no_expired_dataset(self):
        # Set up 3 unexpired datasets
        datasets = [
            UserDatasetFactory(
                expires_at=self.now + timedelta(days=7),
                state=DatasetStates.SUCCEEDED,
                computed_file=DatasetComputedFileFactory(),
            )
            for _ in range(3)
        ]

        self.expire_user_datasets()
        # Should not mark the dataset as expired or delete computed files in the database
        for dataset in datasets:
            updated_dataset = UserDataset.objects.get(id=dataset.id)
            self.assertEqual(
                updated_dataset.state, DatasetStates.SUCCEEDED
            )  # Should remain unchanged
            self.assertIsNotNone(updated_dataset.computed_file)
