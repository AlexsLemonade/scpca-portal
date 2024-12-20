import logging
import time
from typing import Dict, List

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import s3
from scpca_portal.models import OriginalFile

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Sync OriginalFiles with s3 input bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument("--bucket-name", type=str)

    def handle(self, *args, **kwargs):
        bucket_name = kwargs.get("bucket_name", settings.AWS_S3_INPUT_BUCKET_NAME)

        listed_objects = s3.list_bucket_objects(bucket_name)
        self.sync_original_files(listed_objects, bucket_name)

    def sync_original_files(self, file_objects: List[Dict], bucket):
        sync_timestamp = time.time()
        OriginalFile.bulk_create_from_dicts(file_objects, bucket, sync_timestamp)
        # OriginalFile.bulk_update_from_dicts(file_objects, sync_timestamp)
        # OriginalFile.purge_delete_files(sync_timestamp)
