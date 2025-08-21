"""ScPCA portal API token."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from scpca_portal.models.base import TimestampedModel


def validate_email_blacklist(value):
    """
    Prevent the ability to use certain email addresses to create a token.
    This is primarily to prevent pollution from the swagger-ui documentation.
    """
    # Email validation will get this.
    if "@" not in value:
        return

    blacklist = ["example.com"]

    domain = value.split("@").lower()
    if domain in blacklist:
        raise ValidationError(f"Emails from the domain '{domain}' are not allowed.", code="invalid")


class APIToken(TimestampedModel):
    """Controls API user access to the portal data."""

    class Meta:
        db_table = "api_tokens"

    email = models.EmailField("email", validators=[validate_email_blacklist])
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
    def terms_and_conditions(self) -> str:
        """Terms and conditions placeholder."""

        return settings.TERMS_AND_CONDITIONS
