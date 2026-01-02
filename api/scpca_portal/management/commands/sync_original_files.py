from datetime import datetime
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from scpca_portal import lockfile, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import OriginalFile, Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Sync OriginalFile table with s3 input bucket.
    """

    def add_arguments(self, parser):
        parser.add_argument("--bucket", type=str, default=settings.AWS_S3_INPUT_BUCKET_NAME)
        # if all files have been wiped in passed s3 bucket, deletion in db must be manually enabled
        # this is mainly for testing purposes
        parser.add_argument("--allow-bucket-wipe", type=bool, default=False)

    def handle(self, *args, **kwargs):
        self.sync_original_files(**kwargs)

    def get_indented_files(self, files: List[OriginalFile]) -> str:
        formatted_file_str = "\n".join(f"\t{str(f)}" for f in files) if files else "\tNone"
        return formatted_file_str

    def log_file_changes(
        self,
        updated_files: List[OriginalFile],
        created_files: List[OriginalFile],
        deleted_files: List[OriginalFile],
        sync_timestamp,
    ) -> None:
        """Log out stats from the files that changed (updated, created, deleted)"""
        logger.info(
            f"Synced files at {sync_timestamp}.\n"
            f"Updated Files:\n{self.get_indented_files(updated_files)}\n"
            f"Created Files:\n{self.get_indented_files(created_files)}\n"
            f"Deleted Files:\n{self.get_indented_files(deleted_files)}"
        )

    def sync_original_files(self, bucket: str, allow_bucket_wipe: bool, **kwargs):
        logger.info("Initiating listing of bucket objects...")

        locked_project_ids = lockfile.get_locked_project_ids()
        Project.lock_projects(locked_project_ids)

        print(locked_project_ids)

        bucket_objects = s3.list_bucket_objects(bucket, excluded_key_substrings=locked_project_ids)

        logger.info("Syncing database...")
        sync_timestamp = make_aware(datetime.now())

        logger.info("Updating modified existing OriginalFiles.")
        updated_files = OriginalFile.bulk_update_from_dicts(bucket_objects, bucket, sync_timestamp)

        logger.info("Inserting new OriginalFiles.")
        created_files = OriginalFile.bulk_create_from_dicts(bucket_objects, bucket, sync_timestamp)

        logger.info("Purging OriginalFiles that were deleted from s3.")
        deleted_files = OriginalFile.purge_deleted_files(bucket, sync_timestamp, allow_bucket_wipe)

        logger.info("Database syncing complete!")

        self.log_file_changes(updated_files, created_files, deleted_files, sync_timestamp)

        # TODO: send log to slack as well when notification module is set up
