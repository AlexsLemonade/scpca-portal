from django.db import models

from scpca_portal.models.base import TimestampedModel


class ExternalAccession(TimestampedModel):
    """External accession."""

    class Meta:
        db_table = "external_accessions"

    accession = models.TextField(primary_key=True)
    has_raw = models.BooleanField(default=False)
    url = models.TextField()

    def __str__(self) -> str:
        return self.accession
