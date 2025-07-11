from typing import List

from django.conf import settings

from scpca_portal import s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)

LOCKFILE_S3_KEY = "projects.lock"


def get_lockfile_project_ids(*, initial_sync=False) -> List[str]:
    """Return list of all projects ids present in the lockfile."""
    lockfile_original_file = OriginalFile.objects.filter(
        s3_key=LOCKFILE_S3_KEY, s3_bucket=settings.AWS_S3_INPUT_BUCKET_NAME
    ).first()
    # create default lockfile original file in memory
    # if method is called during initial syncing of original files
    if initial_sync:
        lockfile_original_file = OriginalFile(
            s3_key=LOCKFILE_S3_KEY, s3_bucket=settings.AWS_S3_INPUT_BUCKET_NAME
        )

    if lockfile_original_file.size_in_bytes == 0 and not initial_sync:
        return []

    if lockfile_original_file.local_file_path.exists():
        lockfile_original_file.local_file_path.unlink()

    s3.download_files([lockfile_original_file])

    try:
        with lockfile_original_file.local_file_path.open("r", encoding="utf-8") as raw_file:
            lockfile_project_ids = [line.strip() for line in raw_file if line.strip()]
        lockfile_original_file.local_file_path.unlink()
    except FileNotFoundError as error:
        logger.error(f"Lockfile not found: {error}")
        lockfile_project_ids = []

    return lockfile_project_ids
