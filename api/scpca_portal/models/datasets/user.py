from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.datasets import DatasetABC

logger = get_and_configure_logger(__name__)


class UserDataset(DatasetABC):
    class Meta:
        db_table = "user_datasets"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    # Cached File Attrs
    total_sample_count = models.BigIntegerField(default=0)
    diagnoses_summary = models.JSONField(default=dict)
    files_summary = models.JSONField(default=list)  # expects a list of dicts
    project_diagnoses = models.JSONField(default=dict)
    project_modality_counts = models.JSONField(default=dict)
    modality_count_mismatch_projects = ArrayField(models.TextField(), default=list)
    project_sample_counts = models.JSONField(default=dict)
    project_titles = models.JSONField(default=dict)
