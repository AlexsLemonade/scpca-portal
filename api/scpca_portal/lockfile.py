from typing import List

from django.conf import settings

from scpca_portal import s3
from scpca_portal.models import OriginalFile, Project

LOCKFILE_KEY = "projects.lock"
LOCKFILE_PATH = settings.INPUT_DATA_PATH / LOCKFILE_KEY


def get_is_lockfile_empty() -> bool:
    return s3.check_file_empty(LOCKFILE_KEY, settings.AWS_S3_INPUT_BUCKET_NAME)


def get_lockfile_exists_locally() -> bool:
    return LOCKFILE_PATH.exists()


def lock_projects() -> List[str]:
    """
    Iterates through all projects in the lockfile and locks them.
    After all projects are locked, the input lockfile is replaced.
    """

    if get_is_lockfile_empty():
        return []

    if not get_lockfile_exists_locally():
        lockfile_original_file = OriginalFile.objects.filter(
            bucket=settings.AWS_S3_INPUT_BUCKET_NAME, key=LOCKFILE_KEY
        ).first()
        s3.download_files([lockfile_original_file])

    with LOCKFILE_PATH.open("r", encoding="utf-8") as raw_file:
        lockable_project_ids = [line.strip() for line in raw_file if line.strip()]

    lockable_projects = []
    for project_id in lockable_project_ids:
        project = Project.objects.filter(scpca_id=project_id).first()
        project.is_locked = True
        lockable_projects.append(project)
    Project.objects.bulk_update(lockable_projects, ["is_locked"])

    # Replace the remote lockfile with an empty lockfile and delete the local copy
    LOCKFILE_PATH.write_text("", encoding="utf-8")
    s3.upload_file(LOCKFILE_KEY, settings.AWS_S3_INPUT_BUCKET_NAME, LOCKFILE_PATH)
    LOCKFILE_PATH.unlink()

    return lockable_project_ids
