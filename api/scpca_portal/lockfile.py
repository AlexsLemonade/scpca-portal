from typing import List

from django.conf import settings

from scpca_portal import s3
from scpca_portal.config.logging import get_and_configure_logger

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
