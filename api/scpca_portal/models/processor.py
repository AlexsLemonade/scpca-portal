from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel


class Processor(SafeDeleteModel):
    class Meta:
        db_table = "processors"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    objects = SafeDeleteManager()
    deleted_objects = SafeDeleteDeletedManager()
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.TextField(null=False)
    version = models.TextField(null=False)
    workflow_name = models.TextField(null=False)

    is_deleted = models.BooleanField(default=False)

    samples = models.ManyToManyField("Sample", through="SampleProcessorAssociation")
