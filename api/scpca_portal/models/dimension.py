from django.db import models

from scpca_portal.enums import EventResources, EventTypes
from scpca_portal.models.base import TimestampedModel


class Dimension(TimestampedModel):
    class Meta:
        db_table = "dimensions"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["resource", "event_type", "name"],
                name="unique_event_dimensions",
            )
        ]

    resource = models.TextField(choices=EventResources.choices)  # dataset, job
    event_type = models.TextField(choices=EventTypes)

    name = models.TextField()  # e.g., resource_id for both job and dataset
    values = models.JSONField(default=list)  # Available values for this dimension

    def __str__(self) -> str:
        return f"Dimension {self.name} for {self.event_type} - {self.resource}"
