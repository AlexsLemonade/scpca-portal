from django.db import models

from scpca_portal.models.base import TimestampedModel


class Publication(TimestampedModel):
    """Publication class."""

    class Meta:
        db_table = "publications"

    doi = models.TextField(unique=True)
    citation = models.TextField()
    pi_name = models.TextField()

    def __str__(self) -> str:
        return self.doi

    @property
    def doi_url(self):
        """Returns DOI URL."""
        return f"https://doi.org/{self.doi}"
