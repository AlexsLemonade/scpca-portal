from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class TestSyncOriginalFiles(TestCase):
    def setUp(self):
        self.sync_original_files = partial(call_command, "sync_original_files")

        # dummy data mocking the s3 response
        listed_objects = [
            {
                "LastModified": "2024-04-19T18:44:06.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "2024-04-19/SCPCP999990/SCPCP999990_bulk_metadata.tsv",
                "size_in_bytes": 442,
                "hash": "7bf430b2c2832db1405c254553fe5c30",
            },
            {
                "LastModified": "2024-02-21T00:22:08.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "2024-02-20/SCPCP999990/SCPCS999990/SCPCL999990_metadata.json",
                "size_in_bytes": 947,
                "hash": "8b583063ad636f7969f6529abcadc18a",
            },
            {
                "LastModified": "2024-01-11T17:44:32.000Z",
                "StorageClass": "STANDARD",
                "s3_key": "project-metadata-changes/SCPCP999990/SCPCP999990_bulk_metadata.tsv",
                "size_in_bytes": 442,
                "hash": "422956680f050e305588cfe2501fe0b3",
            },
        ]
        # patch s3::list_bucket_objects in each test so that mocked s3 response is the return value
        patcher = patch("scpca_portal.s3", "list_bucket_objects", return_value=listed_objects)
        self.mock_list_bucket_objects = patcher.start()
        self.addCleanup(patcher.stop)
