from pathlib import Path
from typing import Dict, List

from django.conf import settings

from scpca_portal import s3, utils
from scpca_portal.models import OriginalFile, Project

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


def lock_projects() -> List[Project]:
    """Iterate through all projects with ids in the lockfile and lock them."""
    locked_projects = []
    for project_id in get_lockfile_project_ids():
        project = Project.objects.filter(scpca_id=project_id).first()
        project.is_locked = True
        locked_projects.append(project)
    Project.objects.bulk_update(locked_projects, ["is_locked"])

    return locked_projects


def get_unlocked_files(file_objects: List[Dict], locked_project_ids: List[str]):
    unlocked_files = []
    for file_object in file_objects:
        if (
            utils.InputBucketS3KeyInfo(Path(file_object["s3_key"])).project_id
            not in locked_project_ids
        ):
            unlocked_files.append(file_objects)

    return unlocked_files
