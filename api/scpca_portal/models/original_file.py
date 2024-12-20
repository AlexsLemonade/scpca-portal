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
