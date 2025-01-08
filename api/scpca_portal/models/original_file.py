from pathlib import Path
from typing import Dict, List, Set, Tuple

from django.db import models

from typing_extensions import Self

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


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
    is_single_cell = models.BooleanField(default=False)
    is_spatial = models.BooleanField(default=False)
    is_single_cell_experiment = models.BooleanField(default=False)
    is_anndata = models.BooleanField(default=False)
    is_bulk = models.BooleanField(default=False)
    is_merged = models.BooleanField(default=False)
    is_metadata = models.BooleanField(default=False)

    def __str__(self):
        return f"Original File {self.s3_key} from Project {self.project_id} ({self.size_in_bytes}B)"

    @classmethod
    def get_from_dict(cls, file_object, bucket, sync_timestamp):
        s3_key = Path(file_object["s3_key"])

        project_id, sample_id, library_id = OriginalFile.get_relationship_ids(s3_key)
        is_single_cell, is_spatial = OriginalFile.get_modalities(s3_key)
        is_single_cell_experiment, is_anndata, is_metadata = OriginalFile.get_formats(s3_key)
        is_bulk, is_merged = OriginalFile.get_project_file_properties(s3_key)

        original_file = cls(
            s3_bucket=bucket,
            s3_key=s3_key,
            size_in_bytes=file_object["size_in_bytes"],
            hash=file_object["hash"],
            hash_change_at=sync_timestamp,
            bucket_sync_at=sync_timestamp,
            project_id=project_id,
            sample_id=sample_id,
            library_id=library_id,
            is_single_cell=is_single_cell,
            is_spatial=is_spatial,
            is_single_cell_experiment=is_single_cell_experiment,
            is_anndata=is_anndata,
            is_bulk=is_bulk,
            is_merged=is_merged,
            is_metadata=is_metadata,
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

    def update_existing(self, file_object: Dict, sync_timestamp) -> Tuple[Self, Set]:
        """Replace attributes from original instance with those of new instance."""
        updated_fields = {"bucket_sync_at"}
        self.bucket_sync_at = sync_timestamp

        if self.hash is file_object["hash"]:
            return self, updated_fields

        self.hash = file_object["hash"]
        self.hash_change_at = sync_timestamp
        updated_fields.update({"hash", "hash_change_at"})

        if self.size_in_bytes is not file_object["size_in_bytes"]:
            self.size_in_bytes = file_object["size_in_bytes"]
            updated_fields.add("size_in_bytes")

        return self, updated_fields

    @classmethod
    def bulk_update_from_dicts(
        cls, file_objects: List[Dict], bucket: str, sync_timestamp
    ) -> List[Self]:
        updatable_original_files = []
        fields = set()

        for file_object in file_objects:
            if original_instance := OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).first():
                updated_instance, updated_fields = original_instance.update_existing(
                    file_object, sync_timestamp
                )
                updatable_original_files.append(updated_instance)
                fields.update(updated_fields)

        if not updatable_original_files:
            return []

        OriginalFile.objects.bulk_update(updatable_original_files, fields)
        return updatable_original_files

    @staticmethod
    def purge_deleted_files(sync_timestamp) -> List[Self]:
        """Purge all files that no longer exist on s3."""
        # if the last_bucket_sync timestamp wasn't updated,
        # then the file has been deleted from s3, which must be reflected in the db.
        deletable_files = OriginalFile.objects.exclude(bucket_sync_at=sync_timestamp)
        deletable_file_list = list(deletable_files)

        deletable_files.delete()
        return deletable_file_list

    @staticmethod
    def is_project_file(s3_key: Path) -> bool:
        """Checks to see if file is a project data file, and not a library data file."""
        # project files will not have sample subdirectories
        return next((True for p in s3_key.parts if common.SAMPLE_ID_PREFIX in p), False)

    @staticmethod
    def get_relationship_ids(s3_key: Path) -> Tuple:
        """Parses s3_key and returns project, sample and library ids."""
        project_id = next(
            (p for p in s3_key.parts if common.PROJECT_ID_PREFIX in p),
            None,  # the only file w.o. a project id path part should be the projects metadata file
        )
        sample_id = next((p for p in s3_key.parts if common.SAMPLE_ID_PREFIX in p), None)
        library_id = next(
            # library ids are prepended to files followed by an underscore
            (p.split("_")[0] for p in s3_key.parts if common.LIBRARY_ID_PREFIX in p),
            None,
        )

        return project_id, sample_id, library_id

    @staticmethod
    def get_modalities(s3_key: Path) -> Tuple:
        """Returns file modalities using s3_key."""
        is_single_cell, is_spatial = False, False

        if OriginalFile.is_project_file(s3_key):
            return is_single_cell, is_spatial

        # spatial files will have a "spatial" subdirectory
        if next((True for p in s3_key.parts if "spatial" in p), False):
            is_spatial = True
        else:
            is_single_cell = True

        return is_single_cell, is_spatial

    @staticmethod
    def get_formats(s3_key: Path) -> Tuple:
        """Returns file formats using s3_key."""
        is_single_cell_experiment, is_anndata, is_metadata = False, False, False

        if s3_key.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]:
            is_single_cell_experiment = True
        elif s3_key.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]:
            is_anndata = True
        elif s3_key.suffix in [".csv", ".json"]:
            is_metadata = True

        return is_single_cell_experiment, is_anndata, is_metadata

    @staticmethod
    def get_project_file_properties(s3_key: Path) -> Tuple:
        """Returns project file properties using s3_key."""
        is_bulk, is_merged = False, False

        if not OriginalFile.is_project_file(s3_key):
            return is_bulk, is_merged

        if "bulk" in s3_key.parts:
            is_bulk = True
        elif "merged" in s3_key.parts:
            is_merged = True

        return is_bulk, is_merged
