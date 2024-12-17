from django.db import models

from scpca_portal.models import ComputedFile
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

    def __str__(self):
        return f"TrackTokenDownload {self.token}"

    @classmethod
    def track(cls, token_id, computed_file_id):
        if computed_file := ComputedFile.objects.filter(id=computed_file_id).first():

            token_download = TokenDownload.objects.create(
                token=token_id,
                format=computed_file.format,
                modality=computed_file.modality,
                includes_merged=computed_file.includes_merged,
                metadata_only=computed_file.metadata_only,
                portal_metadata_only=computed_file.portal_metadata_only,
            )

            if project := computed_file.project:
                token_download.project_id = project.scpca_id

            if sample := computed_file.sample:
                token_download.sample_id = sample.scpca_id

            token_download.save()
