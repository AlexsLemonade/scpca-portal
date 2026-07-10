from django.db import models

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats
from scpca_portal.models import CCDLDataset
from scpca_portal.models.base import TimestampedModel


class TokenDownload(TimestampedModel):
    class Meta:
        db_table = "track_token_download"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    token = models.TextField()
    project_id = models.TextField(null=True)
    sample_id = models.TextField(null=True)
    format = models.TextField(null=True)
    modality = models.TextField(null=True)
    includes_merged = models.BooleanField(default=False)
    metadata_only = models.BooleanField(default=False)
    portal_metadata_only = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"TrackTokenDownload {self.token}"

    @classmethod
    def track_ccdl_dataset(cls, token_id: str, ccdl_dataset_id: str) -> None:
        if ccdl_dataset := CCDLDataset.objects.filter(id=ccdl_dataset_id).first():

            token_download = TokenDownload.objects.create(
                token=token_id,
                format=ccdl_dataset.format,
                modality=ccdl_dataset.ccdl_modality,
                includes_merged=ccdl_dataset.ccdl_is_merged,
                metadata_only=ccdl_dataset.format == DatasetFormats.METADATA,
                portal_metadata_only=ccdl_dataset.ccdl_name == CCDLDatasetNames.ALL_METADATA,
            )

            token_download.project_id = ccdl_dataset.ccdl_project_id

            token_download.save()
