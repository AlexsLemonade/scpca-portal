"""ScPCA portal API token."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from scpca_portal.models.base import TimestampedModel


class APIToken(TimestampedModel):
    """Controls API user access to the portal data."""

    class Meta:
        db_table = "api_tokens"

    email = models.EmailField("email")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_activated = models.BooleanField(default=False)

    @classmethod
    def verify(cls, token_id):
        """
        Returns APIToken instance for an active token_id. Returns None
        otherwise.
        """
        if not token_id:
            return

        try:
            return cls.objects.get(id=token_id, is_activated=True)
        except (APIToken.DoesNotExist, ValidationError):
            pass

    @property
    def terms_and_conditions(self):
        """Terms and conditions placeholder."""

        return settings.TERMS_AND_CONDITIONS
