from django.db import models

from scpca_portal.models.base import TimestampedModel
from scpca_portal.models import ComputedFile


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

    def __str__(self):
        return f"TrackTokenDownload {self.token}"

    @classmethod
    def track(cls, token_id, computed_file_id):
        if computed_file := ComputedFile.objects.filter(id=computed_file_id).first():
            TokenDownload.objects.create(
                token=token_id,
                project_id=computed_file.project,
                sample_id=computed_file.sample,
                format=computed_file.format,
                modality=computed_file.modality,
                includes_merged=computed_file.includes_merged,
            )
