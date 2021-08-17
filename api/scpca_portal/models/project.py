from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel


class Project(SafeDeleteModel):
    class Meta:
        db_table = "projects"
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
