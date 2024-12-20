import time
from pathlib import Path
from typing import Dict, List

from django.db import models

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
    last_bucket_sync = models.DateTimeField()

    # inferred relationship ids
    project_id = models.TextField()
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
        return f"Original File {self.s3_key} from project {self.project_id} ({self.size_in_bytes}B)"

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
            last_bucket_sync=sync_timestamp,
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
    def bulk_create_from_dicts(cls, file_objects, bucket, sync_timestamp):
        original_files = []
        for file_object in file_objects:
            if not OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).exists():
                original_files.append(
                    OriginalFile.get_from_dict(file_object, bucket, sync_timestamp)
                )

        OriginalFile.objects.bulk_create(original_files)

    @staticmethod
    def sync_files(file_objects: List[Dict], bucket):
        sync_timestamp = time.time()
        OriginalFile.bulk_create_from_dicts(file_objects, bucket, sync_timestamp)
