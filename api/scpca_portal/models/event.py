from django.db import models

from scpca_portal.enums import EventResources, EventTypes
from scpca_portal.models import Dimension
from scpca_portal.models.base import TimestampedModel


class Event(TimestampedModel):
    class Meta:
        db_table = "events"
        get_latest_by = "created_at"
        ordering = ["created_at"]

    # created_at is the event timestamp

    # Fields required upon creation
    resource = models.TextField(choices=EventResources.choices)
    resource_id = models.TextField()
    event_type = models.TextField(choices=EventTypes.choices)

    # Internal use
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # django-ipware
    country = models.TextField(blank=True, default="")  # geoip2
    user_agent = models.TextField(blank=True, default="")

    # Actual dimension values for this event
    dimensions_values = models.JSONField(default=dict)

    # All available dimensions associated with this event
    dimensions = models.ManyToManyField(Dimension, related_name="events")

    def __str__(self) -> str:
        return f"Event {self.id} - {self.event_type} at {self.created_at}"
