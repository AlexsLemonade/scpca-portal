from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

from scpca_portal.models.computed_file import ComputedFile


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

    pi_name = models.TextField(unique=True, null=False)
    title = models.TextField(null=False)
    abstract = models.TextField(null=False)
    contact = models.TextField(null=False)
    disease_timings = models.TextField(null=False)
    diagnoses = models.TextField(blank=True, null=True)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)

    sample_count = models.IntegerField(default=0)

    computed_file = models.OneToOneField(
        ComputedFile, blank=False, null=True, on_delete=models.CASCADE, related_name="project"
    )

    is_deleted = models.BooleanField(default=False)
