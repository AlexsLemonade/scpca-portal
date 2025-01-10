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
    Sync OriginalFile table with s3 input bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)

    def handle(self, *args, **kwargs):
        self.sync_original_files(**kwargs)

    def get_indented_files(self, files: List[OriginalFile]) -> str:
        formatted_file_str = "\n".join(f"\t{str(f)}" for f in files)
        return formatted_file_str

    def log_file_changes(self, updated_files, created_files, deleted_files, sync_timestamp) -> None:
        """Log out stats from the files that changed (updated, created, deleted)"""
        line_divider = "*" * 50
        updated_files_formatted_str = (
            f"Updated Files:\n{self.get_indented_files(updated_files)}" if updated_files else ""
        )
        created_files_formatted_str = (
            f"Created Files:\n{self.get_indented_files(created_files)}" if created_files else ""
        )
        deleted_files_formatted_str = (
            f"Deleted Files:\n{self.get_indented_files(deleted_files)}" if deleted_files else ""
        )

        if updated_files or created_files or deleted_files:
            logger.info(
                f"{line_divider}\n"
                "File Changes Breakdown\n"
                f"{updated_files_formatted_str}\n"
                f"{created_files_formatted_str}\n"
                f"{deleted_files_formatted_str}\n"
                f"{line_divider}"
            )
        else:
            logger.info(
                f"{line_divider}\n"
                "No files have been updated, created, or deleted since the last sync.\n"
                f"{line_divider}"
            )

        logger.info(f"Recent sync_timestamp used: {sync_timestamp}")

    def sync_original_files(self, bucket: str, **kwargs):
        logger.info("Initiating listing of bucket objects...")
        listed_objects = s3.list_bucket_objects(bucket)

        logger.info("Syncing database...")
        sync_timestamp = make_aware(datetime.now())

        logger.info("Updating modified existing OriginalFiles.")
        updated_files = OriginalFile.bulk_update_from_dicts(listed_objects, bucket, sync_timestamp)

        logger.info("Inserting new OriginalFiles.")
        created_files = OriginalFile.bulk_create_from_dicts(listed_objects, bucket, sync_timestamp)

        logger.info("Purging OriginalFiles that were deleted from s3.")
        deleted_files = OriginalFile.purge_deleted_files(bucket, sync_timestamp)

        logger.info("Database syncing complete!")

        self.log_file_changes(updated_files, created_files, deleted_files, sync_timestamp)

        # TODO: send log to slack as well when notification module is set up
