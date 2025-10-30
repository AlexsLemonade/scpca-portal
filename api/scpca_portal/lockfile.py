from typing import List

from django.conf import settings

from scpca_portal import s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)

LOCKFILE_S3_KEY = "projects.lock"
LOCKFILE_FILE_SUFFIX = "lock"


def get_is_locked_project(
    project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
) -> bool:
    project_lockfile = f"{project_id}.{LOCKFILE_FILE_SUFFIX}"
    return s3.check_file_exists(project_lockfile, bucket=bucket)


def get_locked_project_ids(*, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME) -> List[str]:
    project_lockfile_paths = s3.list_files_by_suffix(LOCKFILE_FILE_SUFFIX, bucket=bucket)
    return [path.stem for path in project_lockfile_paths]


def get_lockfile_project_ids_with_file_check(
    *, bucket=settings.AWS_S3_INPUT_BUCKET_NAME
) -> List[str]:
    if s3.check_file_empty(LOCKFILE_S3_KEY, bucket):
        return []
    return get_lockfile_project_ids(bucket=bucket)


def get_lockfile_project_ids(*, bucket=settings.AWS_S3_INPUT_BUCKET_NAME) -> List[str]:
    """Return list of all projects ids present in the lockfile."""
    lockfile_original_file = OriginalFile.objects.filter(
        s3_key=LOCKFILE_S3_KEY, s3_bucket=bucket
    ).first()
    # create default lockfile original file in memory
    # if method is called during initial syncing of original files
    if not lockfile_original_file:
        lockfile_original_file = OriginalFile(s3_key=LOCKFILE_S3_KEY, s3_bucket=bucket)
    # only check size if lockfile original file exists
    elif lockfile_original_file.size_in_bytes == 0:
        return []

    if lockfile_original_file.local_file_path.exists():
        lockfile_original_file.local_file_path.unlink()

    s3.download_files([lockfile_original_file])

    lockfile_project_ids = []
    try:
        with lockfile_original_file.local_file_path.open("r", encoding="utf-8") as raw_file:
            lockfile_project_ids = [line.strip() for line in raw_file if line.strip()]
        lockfile_original_file.local_file_path.unlink()
    except FileNotFoundError as error:
        logger.error(f"Lockfile not found: {error}")

    return lockfile_project_ids
