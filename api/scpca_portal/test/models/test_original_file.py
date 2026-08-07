from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.models import OriginalFile
from scpca_portal.test.factories import OriginalFileFactory


class TestOriginalFile(TestCase):
    def setUp(self):
        self.bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        self.sync_timestamp = make_aware(datetime.now())

    def test_get_syncable_files(self):
        # NO LOCKFILE, ALL FILES SYNCABLE
        bucket_objects = [
            {
                "s3_key": "SCPCP999990/SCPCP999990_bulk_metadata.tsv",
                "size_in_bytes": 442,
                "hash": "7bf430b2c2832db1405c254553fe5c30",
            },
            {
                "s3_key": "SCPCP999990/SCPCS999990/SCPCL999990_metadata.json",
                "size_in_bytes": 947,
                "hash": "8b583063ad636f7969f6529abcadc18a",
            },
        ]

        syncable_original_files, lockfiles = OriginalFile.get_syncable_files(
            bucket_objects, self.bucket, self.sync_timestamp
        )

        self.assertEqual(lockfiles, [])
        self.assertCountEqual(
            [f.s3_key for f in syncable_original_files],
            [bucket_object["s3_key"] for bucket_object in bucket_objects],
        )

        # WITH LOCKFILE, LOCKED PROJECT FILES EXCLUDED
        locked_project_id = "SCPCP999993"
        locked_project_file = {
            "s3_key": f"{locked_project_id}/{locked_project_id}_bulk_metadata.tsv",
            "size_in_bytes": 442,
            "hash": "7bf430b2c2832db1405c254553fe5c30",
        }
        locked_project_lockfile = {
            "s3_key": f"{locked_project_id}.lock",
            "size_in_bytes": 0,
            "hash": "d41d8cd98f00b204e9800998ecf8427e",
        }
        unrelated_file = {
            "s3_key": "SCPCP999990/SCPCP999990_bulk_metadata.tsv",
            "size_in_bytes": 442,
            "hash": "7bf430b2c2832db1405c254553fe5c30",
        }

        syncable_original_files, lockfiles = OriginalFile.get_syncable_files(
            [locked_project_file, locked_project_lockfile, unrelated_file],
            self.bucket,
            self.sync_timestamp,
        )

        syncable_s3_keys = [f.s3_key for f in syncable_original_files]
        self.assertNotIn(locked_project_file["s3_key"], syncable_s3_keys)
        self.assertIn(locked_project_lockfile["s3_key"], syncable_s3_keys)
        self.assertIn(unrelated_file["s3_key"], syncable_s3_keys)
        self.assertEqual(len(lockfiles), 1)
        self.assertEqual(lockfiles[0].s3_key, locked_project_lockfile["s3_key"])
        self.assertEqual(lockfiles[0].project_id, locked_project_id)

    def test_bulk_create(self):
        new_file = OriginalFileFactory.build(s3_key="new.txt")
        existing_file = OriginalFileFactory(s3_key="existing.txt")
        duplicate_file = OriginalFileFactory.build(s3_key=existing_file.s3_key)

        created_files = OriginalFile.bulk_create([new_file, duplicate_file])

        self.assertListEqual([f.s3_key for f in created_files], ["new.txt"])
        self.assertEqual(OriginalFile.objects.filter(s3_key=existing_file.s3_key).count(), 1)
        self.assertTrue(OriginalFile.objects.filter(s3_key="new.txt").exists())

    def test_bulk_update(self):
        # MODIFIED FILE GETS HASH, SIZE, HASH_SYNCED_AT AND BUCKET_SYNCED_AT UPDATED
        existing_file = OriginalFileFactory(s3_key="file.txt", hash="original-hash")
        new_sync_timestamp = make_aware(datetime.now())
        modified_file = OriginalFileFactory.build(
            s3_key=existing_file.s3_key,
            hash="new-hash",
            size_in_bytes=999,
            hash_change_at=new_sync_timestamp,
            bucket_sync_at=new_sync_timestamp,
        )

        modified_files = OriginalFile.bulk_update([modified_file])

        self.assertEqual([f.s3_key for f in modified_files], ["file.txt"])
        existing_file.refresh_from_db()
        self.assertEqual(existing_file.hash, "new-hash")
        self.assertEqual(existing_file.size_in_bytes, 999)
        self.assertEqual(existing_file.hash_change_at, new_sync_timestamp)
        self.assertEqual(existing_file.bucket_sync_at, new_sync_timestamp)

        OriginalFile.objects.all().delete()

        # UNMODIFIED FILE GETS ONLY BUCKET_SYNCED_AT UPDATED
        existing_file = OriginalFileFactory(s3_key="file.txt", hash="same-hash")
        original_hash_change_at = existing_file.hash_change_at
        new_sync_timestamp = make_aware(datetime.now())
        unmodified_file = OriginalFileFactory.build(
            s3_key=existing_file.s3_key, hash="same-hash", bucket_sync_at=new_sync_timestamp
        )

        modified_files = OriginalFile.bulk_update([unmodified_file])

        self.assertEqual(modified_files, [])
        existing_file.refresh_from_db()
        self.assertEqual(existing_file.hash_change_at, original_hash_change_at)
        self.assertEqual(existing_file.bucket_sync_at, new_sync_timestamp)

        OriginalFile.objects.all().delete()

        # NEW FILE IS SKIPPED
        never_synced_file = OriginalFileFactory.build(s3_key="never-synced.txt")

        modified_files = OriginalFile.bulk_update([never_synced_file])

        self.assertEqual(modified_files, [])
        self.assertFalse(OriginalFile.objects.filter(s3_key="never-synced.txt").exists())

    def test_purge_deleted_files(self):
        stale_sync_timestamp = self.sync_timestamp - timedelta(days=1)

        # ONLY STALE FILES (NOT SYNCED THIS ROUND) ARE PURGED
        stale_file = OriginalFileFactory(bucket_sync_at=stale_sync_timestamp)
        synced_file = OriginalFileFactory(bucket_sync_at=self.sync_timestamp)

        deleted_files = OriginalFile.purge_deleted_files(self.bucket, self.sync_timestamp, [])

        self.assertEqual([f.pk for f in deleted_files], [stale_file.pk])
        self.assertFalse(OriginalFile.objects.filter(pk=stale_file.pk).exists())
        self.assertTrue(OriginalFile.objects.filter(pk=synced_file.pk).exists())

        OriginalFile.objects.all().delete()

        # LOCKED PROJECT'S FILES ARE PROTECTED FROM PURGING
        locked_project_id = "SCPCP999993"
        stale_locked_file = OriginalFileFactory(
            project_id=locked_project_id, bucket_sync_at=stale_sync_timestamp
        )
        stale_unlocked_file = OriginalFileFactory(bucket_sync_at=stale_sync_timestamp)

        deleted_files = OriginalFile.purge_deleted_files(
            self.bucket, self.sync_timestamp, [locked_project_id]
        )

        self.assertEqual([f.pk for f in deleted_files], [stale_unlocked_file.pk])
        self.assertTrue(OriginalFile.objects.filter(pk=stale_locked_file.pk).exists())
        self.assertFalse(OriginalFile.objects.filter(pk=stale_unlocked_file.pk).exists())

        OriginalFile.objects.all().delete()

        # A FULL BUCKET WIPE IS BLOCKED WITHOUT ALLOW_BUCKET_WIPE
        stale_file = OriginalFileFactory(bucket_sync_at=stale_sync_timestamp)

        deleted_files = OriginalFile.purge_deleted_files(self.bucket, self.sync_timestamp, [])

        self.assertEqual(deleted_files, [])
        self.assertTrue(OriginalFile.objects.filter(pk=stale_file.pk).exists())

        # A FULL BUCKET WIPE IS ALLOWED WITH ALLOW_BUCKET_WIPE PASSED
        deleted_files = OriginalFile.purge_deleted_files(
            self.bucket, self.sync_timestamp, [], allow_bucket_wipe=True
        )

        self.assertEqual([f.pk for f in deleted_files], [stale_file.pk])
        self.assertFalse(OriginalFile.objects.exists())
