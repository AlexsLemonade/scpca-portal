from abc import abstractmethod
from typing import List, Self

from django.db import models

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class AggregatableResourceABC(TimestampedModel):
    class Meta:
        abstract = True

    aggregation_hash = models.CharField(max_length=32, null=True)

    @classmethod
    def sync_aggregations(cls) -> int:
        needs_aggregation_resources = cls.get_needs_aggregation_resources()

        for resource in needs_aggregation_resources:
            resource.update_aggregations()
            resource.aggregation_hash = resource.current_aggregation_hash

        fields_to_update = [f.name for f in cls._meta.concrete_fields if not f.primary_key]
        return cls.objects.bulk_update(needs_aggregation_resources, fields=fields_to_update)

    @classmethod
    @abstractmethod
    def get_needs_aggregation_resources(cls) -> List[Self]:
        pass

    @property
    def needs_aggregation(self) -> bool:
        return self.aggregation_hash != self.current_aggregation_hash

    @property
    @abstractmethod
    def current_aggregation_hash(self) -> str:
        pass

    @abstractmethod
    def update_aggregations(self) -> None:
        pass
