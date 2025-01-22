from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.models import OriginalFile


class TestSyncOriginalFiles(TestCase):
    def setUp(self):
        self.sync_original_files = partial(call_command, "sync_original_files")

        # dummy data mocking the s3 response
        self.original_objects_list = [
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
            {
                "LastModified": "2024-01-11T17:44:32.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad",
                "size_in_bytes": 801,
                "hash": "422956680f050e305588cfe2501fe0b3",
            },
            {
                "LastModified": "2024-10-01T21:23:24.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json",
                "size_in_bytes": 544,
                "hash": "03f55d5cc6ff64352bbcc2a3a7b72ac7",
            },
        ]

        self.modified_objects_list = [
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
                "hash": "modified_hash",
            },
            {
                "LastModified": "2024-01-11T17:44:32.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad",
                "size_in_bytes": 801,
                "hash": "modified_hash",
            },
        ]

        self.empty_objects_list = []

    def test_sync_original_files(self):
        self.assertFalse(OriginalFile.objects.exists())

        # TEST ORIGINAL FILE CREATION
        with patch("scpca_portal.s3.list_bucket_objects", return_value=self.original_objects_list):
            self.sync_original_files()
        self.assertEqual(OriginalFile.objects.count(), len(self.original_objects_list))
        first_sync_timestamp = OriginalFile.objects.first().bucket_sync_at

        # TEST ORIGINAL FILE UPDATING AND SINGLE FILE DELETION
        with patch("scpca_portal.s3.list_bucket_objects", return_value=self.modified_objects_list):
            self.sync_original_files()
        second_sync_timestamp = OriginalFile.objects.first().bucket_sync_at

        # assert that correct numbers of files exist, and correct number were deleted
        self.assertEqual(OriginalFile.objects.count(), len(self.modified_objects_list))

        non_modified_files = OriginalFile.objects.filter(hash_change_at=first_sync_timestamp)
        self.assertListEqual(
            sorted(
                file.get("s3_key")
                for file in self.modified_objects_list
                if file.get("hash") != "modified_hash"
            ),
            sorted(non_modified_files.values_list("s3_key", flat=True)),
        )

        modified_files = OriginalFile.objects.filter(hash_change_at=second_sync_timestamp)
        self.assertListEqual(
            sorted(
                file.get("s3_key")
                for file in self.modified_objects_list
                if file.get("hash") == "modified_hash"
            ),
            sorted(modified_files.values_list("s3_key", flat=True)),
        )

        # TEST ATTEMPTED DELETION OF ALL FILES - allow_bucket_wipe flag NOT passed
        with patch("scpca_portal.s3.list_bucket_objects", return_value=self.empty_objects_list):
            self.sync_original_files()
        self.assertListEqual(
            sorted(file.get("s3_key") for file in self.modified_objects_list),
            sorted(OriginalFile.objects.all().values_list("s3_key", flat=True)),
        )

        # TEST SUCCESSFUL DELETION OF ALL FILES - allow_bucket_wipe flag passed
        with patch("scpca_portal.s3.list_bucket_objects", return_value=self.empty_objects_list):
            self.sync_original_files(allow_bucket_wipe=True)
        self.assertFalse(OriginalFile.objects.exists())
