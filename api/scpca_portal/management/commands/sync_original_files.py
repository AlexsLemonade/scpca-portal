import logging
from datetime import datetime
from typing import List

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

    def generate_formatted_file_string(self, files: List[OriginalFile], file_type: str) -> str:
        if not files:
            return ""

        formatted_file_str = f"{file_type}:\n"
        formatted_file_str += "\n".join(f"- {str(f)}" for f in files) if files else "- None"
        formatted_file_str += "\n"
        return formatted_file_str

    def sync_original_files(self, bucket_name: str, **kwargs):
        logger.info("Initiating listing of bucket objects...")
        listed_objects = s3.list_bucket_objects(bucket_name)

        logger.info("Syncing database...")
        sync_timestamp = make_aware(datetime.now())

        logger.info("Updating modified existing OriginalFiles.")
        updated_files = OriginalFile.bulk_update_from_dicts(
            listed_objects, bucket_name, sync_timestamp
        )

        logger.info("Inserting new OriginalFiles.")
        created_files = OriginalFile.bulk_create_from_dicts(
            listed_objects, bucket_name, sync_timestamp
        )

        logger.info("Purging OriginalFiles that were deleted from s3.")
        deleted_files = OriginalFile.purge_deleted_files(sync_timestamp)

        logger.info("Database syncing complete!")

        # log out states from the files that changed (updated, created, deleted)
        if updated_files or created_files or deleted_files:
            logger.info(
                "\nFile Changes Breakdown\n"
                f"{self.generate_formatted_file_string(updated_files, 'Updated Files')}"
                f"{self.generate_formatted_file_string(created_files, 'Created Files')}"
                f"{self.generate_formatted_file_string(deleted_files, 'Deleted Files')}"
            )

        # TODO: send log to slack as well when notification module is set up
