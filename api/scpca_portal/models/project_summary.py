from django.db import models

from scpca_portal.models.base import TimestampedModel


class ProjectSummary(TimestampedModel):
    """One of multiple summaries of a project.

    There will be one of these per project samples `diagnosis`,
    each sample's libraries `seq_unit` and `technology`.
    `sample_count` denotes how many samples in the project have those values.
    For example:
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

    diagnosis = models.TextField(blank=True, null=True)
    sample_count = models.PositiveIntegerField(default=0)
    seq_unit = models.TextField(blank=True, null=True)
    technology = models.TextField(blank=True, null=True)

    project = models.ForeignKey(
        "Project", blank=False, null=True, on_delete=models.CASCADE, related_name="summaries"
    )
