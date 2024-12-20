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
    Sync OriginalFiles with s3 input bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument("--bucket-name", type=str)

    def handle(self, *args, **kwargs):
        listed_objects = s3.list_bucket_objects("scpca-local-data")
        OriginalFile.sync_files(
            listed_objects, kwargs.get("bucket_name", settings.AWS_S3_INPUT_BUCKET_NAME)
        )
