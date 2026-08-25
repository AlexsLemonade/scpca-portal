from abc import abstractmethod

from django.db import models

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class AggregatableResourceABC(TimestampedModel):
    class Meta:
        abstract = True

    aggregation_hash = models.CharField(max_length=32, null=True)

    @classmethod
    @abstractmethod
    def sync_aggregations(cls) -> None:
        pass

    @property
    @abstractmethod
    def needs_aggregations(self) -> bool:
        return self.current_aggregation_hash != self.aggregation_hash

    @property
    @abstractmethod
    def current_aggregation_hash(self) -> str:
        pass

    @abstractmethod
    def update_aggregations(self) -> None:
        pass
