from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from django.db import models

from typing_extensions import Self

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class DownloadableFileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_downloadable=True)


class OriginalFile(TimestampedModel):
    class Meta:
        db_table = "original_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    # s3 info
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    hash = models.CharField(max_length=33)
    hash_change_at = models.DateTimeField()
    bucket_sync_at = models.DateTimeField()

    # inferred relationship ids
    project_id = models.TextField(null=True)
    sample_id = models.TextField(null=True)
    library_id = models.TextField(null=True)

    # existence attributes
    # modalities
    is_single_cell = models.BooleanField(default=False)
    is_spatial = models.BooleanField(default=False)
    is_cite_seq = models.BooleanField(default=False)  # indicates if file is exclusively cite_seq
    is_bulk = models.BooleanField(default=False)
    # formats
    is_single_cell_experiment = models.BooleanField(default=False)
    is_anndata = models.BooleanField(default=False)
    is_metadata = models.BooleanField(default=False)
    # other
    is_merged = models.BooleanField(default=False)
    is_project_file = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    # queryset managers
    objects = models.Manager()
    downloadable_objects = DownloadableFileManager()

    def __str__(self):
        return f"Original File {self.s3_key} from Project {self.project_id} ({self.size_in_bytes}B)"

    @classmethod
    def get_from_dict(cls, file_object, bucket, sync_timestamp):
        s3_key_info = S3KeyInfo(Path(file_object["s3_key"]))

        original_file = cls(
            s3_bucket=bucket,
            s3_key=file_object["s3_key"],
            size_in_bytes=file_object["size_in_bytes"],
            hash=file_object["hash"],
            hash_change_at=sync_timestamp,
            bucket_sync_at=sync_timestamp,
            project_id=s3_key_info.project_id,
            sample_id=s3_key_info.sample_id,
            library_id=s3_key_info.library_id,
            is_single_cell=s3_key_info.is_single_cell,
            is_spatial=s3_key_info.is_spatial,
            is_cite_seq=s3_key_info.is_cite_seq,
            is_bulk=s3_key_info.is_bulk,
            is_single_cell_experiment=s3_key_info.is_single_cell_experiment,
            is_anndata=s3_key_info.is_anndata,
            is_metadata=s3_key_info.is_metadata,
            is_merged=s3_key_info.is_merged,
            is_project_file=s3_key_info.is_project_file,
            is_downloadable=s3_key_info.is_downloadable,
        )

        return original_file

    @classmethod
    def bulk_create_from_dicts(cls, file_objects, bucket, sync_timestamp) -> List[Self]:
        original_files = []
        for file_object in file_objects:
            if not OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).exists():
                original_files.append(
                    OriginalFile.get_from_dict(file_object, bucket, sync_timestamp)
                )

        return OriginalFile.objects.bulk_create(original_files)

    @classmethod
    def bulk_update_from_dicts(
        cls, file_objects: List[Dict], bucket: str, sync_timestamp
    ) -> List[Self]:
        # all existing files must have their timestamps updated, at the minimum
        existing_original_files = []
        # existing files that have been modified should be collected and returned separately
        modified_original_files = []
        fields = set()

        for file_object in file_objects:
            if original_instance := OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).first():
                if original_instance.hash != file_object["hash"]:
                    original_instance.hash = file_object["hash"]
                    original_instance.hash_change_at = sync_timestamp
                    original_instance.size_in_bytes = file_object["size_in_bytes"]
                    fields.update({"hash", "hash_change_at", "size_in_bytes"})

                    modified_original_files.append(original_instance)

                # all existing objects with files still on s3 must have their timestamps updated
                original_instance.bucket_sync_at = sync_timestamp
                fields.add("bucket_sync_at")

                existing_original_files.append(original_instance)

        # check that file_objects are not all new files (bulk_update will fail with an empty list)
        if existing_original_files:
            OriginalFile.objects.bulk_update(existing_original_files, fields)

        return modified_original_files

    @staticmethod
    def purge_deleted_files(
        bucket: str, sync_timestamp, allow_bucket_wipe: bool = False
    ) -> List[Self]:
        """Purge all files that no longer exist on s3."""
        # if the last_bucket_sync timestamp wasn't updated,
        # then the file has been deleted from s3, which must be reflected in the db.
        deletable_files = OriginalFile.objects.filter(s3_bucket=bucket).exclude(
            bucket_sync_at=sync_timestamp
        )
        deletable_file_list = list(deletable_files)

        all_bucket_files = OriginalFile.objects.filter(s3_bucket=bucket)
        # if allow_bucket_wipe flag is not passed, do not allow all bucket files to be wiped
        if set(all_bucket_files) == set(deletable_files) and not allow_bucket_wipe:
            return []

        deletable_files.delete()
        return deletable_file_list

    @property
    def s3_absolute_path(self) -> Path:
        return Path(self.s3_bucket) / Path(self.s3_key)

    @property
    def download_dir(self) -> Path:
        """
        Return an original file's download directory.

        To produce more efficient downloads, files are downloaded as collections.
        Collections are formed as granularly as possible,
        at either the sample/merged/bulk, project, or bucket levels.
        """
        PROJECT_DIR_PART_COUNT = 1
        SAMPLE_DIR_PART_COUNT = 2

        s3_key_path = Path(self.s3_key)
        dir_part_count = len(s3_key_path.parts) - 1  # remove file itself

        if dir_part_count >= SAMPLE_DIR_PART_COUNT:
            return Path(self.s3_bucket, *s3_key_path.parts[:2])  # bucket/project/sample/

        if dir_part_count == PROJECT_DIR_PART_COUNT:
            return Path(self.s3_bucket, *s3_key_path.parts[:1])  # bucket/project/

        # default to bucket dir
        return Path(self.s3_bucket)  # bucket/

    @property
    def download_path(self) -> Path:
        return self.s3_absolute_path.relative_to(self.download_dir)


@dataclass
class S3KeyInfo:
    s3_key: Path
    project_id: str | None
    sample_id: str | None
    library_id_part: str | None
    is_merged: bool
    is_bulk: bool

    def __init__(self, s3_key: Path):
        self.s3_key = s3_key
        self.project_id = utils.find_first_contained(common.PROJECT_ID_PREFIX, s3_key.parts)
        self.sample_id = utils.find_first_contained(common.SAMPLE_ID_PREFIX, s3_key.parts)
        self.library_id_part = utils.find_first_contained(common.LIBRARY_ID_PREFIX, s3_key.parts)
        self.is_merged = "merged" in s3_key.parts
        self.is_bulk = "bulk" in s3_key.parts

    @property
    def library_id(self):
        if self.library_id_part:
            return self.library_id_part.split("_")[0]
        return self.library_id_part

    @property
    def is_project_file(self):
        """Project files have project dirs but don't have sample dirs"""
        return bool(self.project_id and not self.sample_id)

    @property
    def is_spatial(self):
        # all spatial files have "spatial" appended to the libary part of their file path
        return bool(self.library_id_part and self.library_id_part.endswith("spatial"))

    @property
    def is_single_cell(self):
        # single cell files won't be nested in subdirectories
        return self.library_id_part == self.s3_key.name

    @property
    def is_cite_seq(self):
        return self.s3_key.name.endswith(common.CITE_SEQ_FILENAME_ENDING)

    @property
    def is_single_cell_experiment(self):
        return (
            self.s3_key.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]
            or self.is_spatial  # we consider all spatial files SCE
        )

    @property
    def is_anndata(self):
        return self.s3_key.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]

    @property
    def is_metadata(self):
        return self.s3_key.suffix in common.METADATA_EXTENSIONS

    @property
    def is_downloadable(self):
        """
        Returns whether or not a file is_downloadable.
        Most files are downloadable files,
        the only exceptions are single_cell metadata files and project level metadata files.
        """
        if self.is_single_cell:
            # single_cell metadata files are not included in computed files
            return not self.is_metadata

        return self.s3_key.name not in common.NON_DOWNLOADABLE_PROJECT_FILES
