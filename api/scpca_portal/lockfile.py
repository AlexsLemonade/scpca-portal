from typing import List

from django.conf import settings

from scpca_portal import s3
from scpca_portal.models import OriginalFile

LOCKFILE_KEY = "projects.lock"
LOCKFILE_PATH = settings.INPUT_DATA_PATH / LOCKFILE_KEY


def get_lockfile_project_ids() -> List[str]:
    """Return list of all projects ids present in the lockfile."""
    if s3.check_file_empty(LOCKFILE_KEY, settings.AWS_S3_INPUT_BUCKET_NAME):
        return []

    if LOCKFILE_PATH.exists:
        LOCKFILE_PATH.unlink()

    lockfile_original_file = OriginalFile.objects.filter(
        bucket=settings.AWS_S3_INPUT_BUCKET_NAME, key=LOCKFILE_KEY
    ).first()
    s3.download_files([lockfile_original_file])

    with LOCKFILE_PATH.open("r", encoding="utf-8") as raw_file:
        lockfile_project_ids = [line.strip() for line in raw_file if line.strip()]
    LOCKFILE_PATH.unlink()

    return lockfile_project_ids
