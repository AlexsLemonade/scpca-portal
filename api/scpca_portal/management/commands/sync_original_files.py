import logging
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

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
        logger.info("Initiating listing of bucket objects...")
        listed_objects = s3.list_bucket_objects(bucket_name)

        logger.info("Syncing database...")
        sync_timestamp = make_aware(datetime.now())

        logger.info("Updating modified existing OriginalFiles.")
        OriginalFile.bulk_update_from_dicts(listed_objects, bucket_name, sync_timestamp)

        logger.info("Inserting new OriginalFiles.")
        OriginalFile.bulk_create_from_dicts(listed_objects, bucket_name, sync_timestamp)

        logger.info("Purging OriginalFiles that were deleted from s3.")
        OriginalFile.purge_deleted_files(sync_timestamp)

        logger.info("Database syncing complete!")

        # log out states from the files that changed (updated, created, deleted)

        # TODO: send log to slack as well when notification module is set up
