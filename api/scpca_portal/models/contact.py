from django.db import models

from scpca_portal.models.base import TimestampedModel


class Contact(TimestampedModel):
    """Contact class."""

    class Meta:
        db_table = "contacts"

    name = models.TextField()
    email = models.EmailField(unique=True)
    submitter_id = models.TextField()

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
