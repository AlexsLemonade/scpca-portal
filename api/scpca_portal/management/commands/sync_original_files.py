import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal import s3
from scpca_portal.models import OriginalFile

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Sync OriginalFiles table with s3 input bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument("--bucket-name", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)

    def handle(self, *args, **kwargs):
        self.sync_original_files(**kwargs)

    def sync_original_files(self, bucket_name: str, **kwargs):
        listed_objects = s3.list_bucket_objects(bucket_name)
        OriginalFile.sync(listed_objects, bucket_name)
