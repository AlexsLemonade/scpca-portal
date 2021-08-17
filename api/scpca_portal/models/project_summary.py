from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

from scpca_portal.models.project import Project


class ProjectSummary(SafeDeleteModel):
    class Meta:
        db_table = "project_summaries"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    objects = SafeDeleteManager()
    deleted_objects = SafeDeleteDeletedManager()
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    diagnosis = models.TextField(blank=True, null=True)
    seq_unit = models.TextField(blank=True, null=True)
    technology = models.TextField(blank=True, null=True)

    sample_count = models.IntegerField()

    is_deleted = models.BooleanField(default=False)

    project = models.ForeignKey(
        Project, blank=False, null=True, on_delete=models.CASCADE, related_name="summaries"
    )
