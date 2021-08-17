from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

from scpca_portal.models.processor import Processor
from scpca_portal.models.project import Project
from scpca_portal.models.sample import Sample


class ComputedFile(SafeDeleteModel):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    objects = SafeDeleteManager()
    deleted_objects = SafeDeleteDeletedManager()
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    type = models.TextField(null=False)
    s3_bucket = models.TextField(null=False)
    s3_key = models.TextField(null=False)

    is_deleted = models.BooleanField(default=False)

    processor = models.ForeignKey(
        Processor, blank=False, null=True, on_delete=models.CASCADE, related_name="computed_files"
    )
    project = models.ForeignKey(
        Project, blank=False, null=True, on_delete=models.CASCADE, related_name="computed_files"
    )
    sample = models.ForeignKey(
        Sample, blank=False, null=True, on_delete=models.CASCADE, related_name="computed_files"
    )
