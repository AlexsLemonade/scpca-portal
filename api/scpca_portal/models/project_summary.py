from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

from scpca_portal.models.project import Project


class ProjectSummary(SafeDeleteModel):
    """One of multiple summaries of a project.

    There will be one of these per combination of `diagnosis`,
    `seq_unit`, and `technology`. `sample_count` denotes how many
    samples in the project have those values. For example:
        diagnosis=AML
        seq_unit=cell
        technology=10Xv2_5prime
        sample_count=28

    indicates that this project has 28 samples diagnosed with AML that
    were sequenced at the cell level using 10Xv2_5prime.
    """

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
