from django.db import models

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)


class LoadableResourceABC(models.Model):
    class Meta:
        abstract = True

    state = models.TextField()
    hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)
