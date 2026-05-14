from datetime import datetime, timedelta
from functools import partial

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.models import UserDataset
from scpca_portal.test.factories import UserDatasetFactory


class TestExpireUserDatasets(TestCase):
    def setUp(self):
        self.expire_user_datasets = partial(call_command, "expire_user_datasets")
        self.now = make_aware(datetime.now())

    def test_mark_expired_dataset(self):
        dataset = UserDatasetFactory(
            expires_at=None,
            is_expired=False,
            is_succeeded=True,
            succeeded_at=self.now - timedelta(days=8),
        )

        self.expire_user_datasets()
        # Should set the timestamp and mark as the dataset expired
        expired_dataset = UserDataset.objects.get(id=dataset.id)
        self.assertEqual(
            expired_dataset.expires_at, expired_dataset.succeeded_at + timedelta(days=7)
        )
        self.assertTrue(expired_dataset.is_expired)

    def test_mark_no_expired_dataset(self):
        dataset = UserDatasetFactory(
            expires_at=None, is_expired=False, is_succeeded=True, succeeded_at=self.now
        )

        self.expire_user_datasets()
        # Should only set the timestamp
        updated_dataset = UserDataset.objects.get(id=dataset.id)
        self.assertEqual(
            updated_dataset.expires_at, updated_dataset.succeeded_at + timedelta(days=7)
        )
        self.assertFalse(updated_dataset.is_expired)
