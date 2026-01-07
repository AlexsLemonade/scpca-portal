from django.db import models

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import CCDLDatasetNames, Modalities
from scpca_portal.models.datasets import DatasetABC

logger = get_and_configure_logger(__name__)


class CCDLDataset(DatasetABC):
    class Meta:
        db_table = "ccdl_datasets"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    ccdl_name = models.TextField(choices=CCDLDatasetNames.choices, null=True)
    ccdl_project_id = models.TextField(null=True)
    ccdl_modality = models.TextField(choices=Modalities.choices, null=True)
