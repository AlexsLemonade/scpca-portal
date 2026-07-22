from datetime import datetime, timedelta
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import JobStates
from scpca_portal.models import UserDataset
from scpca_portal.test.factories import DatasetComputedFileFactory, JobFactory, UserDatasetFactory


class TestCleanUpExpiredUserDatasets(TestCase):
    def setUp(self):
        self.clean_up_expired_user_datasets = partial(
            call_command, "clean_up_expired_user_datasets"
        )
        self.now = make_aware(datetime.now())

    @patch("scpca_portal.s3.aws_s3.delete_object")
    def test_clean_up_expired_datasets(self, mock_delete_object):
        datasets = [
            UserDatasetFactory(computed_file=DatasetComputedFileFactory()) for _ in range(3)
        ]
        # Populate the corresponding jobs
        for dataset in datasets:
            JobFactory(
                dataset=dataset,
                state=JobStates.SUCCEEDED,
                succeeded_at=self.now - timedelta(days=9),
            )

        self.clean_up_expired_user_datasets()
        # Should set the timestamp and mark all datasets as expired
        for dataset in datasets:
            updated_dataset = UserDataset.objects.get(id=dataset.id)
            self.assertEqual(updated_dataset.expires_at, dataset.expiration_delta)
            self.assertTrue(updated_dataset.is_expired)
            # Should purge the computed file
            mock_delete_object.assert_called_with(
                Bucket=dataset.computed_file.s3_bucket, Key=dataset.computed_file.s3_key
            )
            self.assertEqual(mock_delete_object.call_count, 3)
            self.assertIsNone(updated_dataset.computed_file)

    @patch("scpca_portal.s3.aws_s3.delete_object")
    def test_no_clean_up_expired_datasets(self, mock_delete_object):
        dataset = UserDatasetFactory(computed_file=DatasetComputedFileFactory())
        # Populate the corresponding job
        JobFactory(dataset=dataset, state=JobStates.SUCCEEDED, succeeded_at=self.now)

        self.clean_up_expired_user_datasets()
        # Should only populate the timestamp and not mark as expired
        updated_dataset = UserDataset.objects.get(id=dataset.id)
        self.assertEqual(updated_dataset.expires_at, dataset.expiration_delta)
        self.assertFalse(updated_dataset.is_expired)
        # Should not purge the computed file
        mock_delete_object.assert_not_called()
        self.assertIsNotNone(updated_dataset.computed_file)
