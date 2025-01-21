from copy import deepcopy
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.models import OriginalFile


class TestSyncOriginalFiles(TestCase):
    def setUp(self):
        self.sync_original_files = partial(call_command, "sync_original_files")

        # dummy data mocking the s3 response
        self.listed_objects = [
            {
                "LastModified": "2024-04-19T18:44:06.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCP999990_bulk_metadata.tsv",
                "size_in_bytes": 442,
                "hash": "7bf430b2c2832db1405c254553fe5c30",
            },
            {
                "LastModified": "2024-02-21T00:22:08.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCS999990/SCPCL999990_metadata.json",
                "size_in_bytes": 947,
                "hash": "8b583063ad636f7969f6529abcadc18a",
            },
            {
                "LastModified": "2024-01-11T17:44:32.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds",
                "size_in_bytes": 770,
                "hash": "422956680f050e305588cfe2501fe0b3",
            },
        ]

    def test_sync_original_files(self):
        self.assertFalse(OriginalFile.objects.exists())

        # test original file creation
        with patch("scpca_portal.s3.list_bucket_objects", return_value=self.listed_objects):
            self.sync_original_files()
        self.assertEqual(OriginalFile.objects.count(), len(self.listed_objects))
        first_sync_timestamp = OriginalFile.objects.first().bucket_sync_at

        # test originnal file updating
        updatable_objects = deepcopy(self.listed_objects)
        updatable_objects[-1]["hash"] = "updated_hash"
        with patch("scpca_portal.s3.list_bucket_objects", return_value=updatable_objects):
            self.sync_original_files()
        second_sync_timestamp = OriginalFile.objects.first().bucket_sync_at

        updated_files = OriginalFile.objects.filter(hash_change_at=second_sync_timestamp)
        non_updated_files = OriginalFile.objects.filter(hash_change_at=first_sync_timestamp)

        self.assertEqual(updated_files.count(), 1)
        self.assertNotIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[0]["s3_key"]).first(),
            updated_files,
        )
        self.assertNotIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[1]["s3_key"]).first(),
            updated_files,
        )
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[2]["s3_key"]).first(),
            updated_files,
        )

        self.assertEqual(non_updated_files.count(), 2)
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[0]["s3_key"]).first(),
            non_updated_files,
        )
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[1]["s3_key"]).first(),
            non_updated_files,
        )
        self.assertNotIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[2]["s3_key"]).first(),
            non_updated_files,
        )

        # test original file deletion of one file
        deletable_objects = deepcopy(self.listed_objects)
        deletable_objects.pop()
        with patch("scpca_portal.s3.list_bucket_objects", return_value=deletable_objects):
            self.sync_original_files()
        remaining_files = OriginalFile.objects.all()
        self.assertEqual(remaining_files.count(), 2)
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[0]["s3_key"]).first(),
            remaining_files,
        )
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[1]["s3_key"]).first(),
            remaining_files,
        )

        # test original file attempted deletion of all files - allow_bucket_wipe flag NOT passed
        with patch("scpca_portal.s3.list_bucket_objects", return_value=[]):
            self.sync_original_files()
        remaining_files = OriginalFile.objects.all()
        self.assertEqual(remaining_files.count(), 2)
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[0]["s3_key"]).first(),
            remaining_files,
        )
        self.assertIn(
            OriginalFile.objects.filter(s3_key=self.listed_objects[1]["s3_key"]).first(),
            remaining_files,
        )

        # test original file deletion of all files - allow_bucket_wipe flag passed
        with patch("scpca_portal.s3.list_bucket_objects", return_value=[]):
            self.sync_original_files(allow_bucket_wipe=True)
        self.assertFalse(OriginalFile.objects.exists())
