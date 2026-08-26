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
    def sync_aggregations(cls, synced_resource_ids: List[str]) -> None:
        aggregating_resources = cls.get_aggregating_resources(synced_resource_ids)

        for resource in aggregating_resources:
            resource.update_aggregations()
            resource.aggregation_hash = resource.current_aggregation_hash

        fields_to_update = [f.name for f in cls._meta.concrete_fields if not f.primary_key]
        cls.objects.bulk_update(aggregating_resources, fields=fields_to_update)

    @classmethod
    def get_aggregating_resources(cls, synced_resource_ids: List[str]) -> List[Self]:
        return [
            resource
            for resource in cls.objects.filter(scpca_id__in=synced_resource_ids)
            if resource.needs_aggregations
        ]

    @property
    @abstractmethod
    def needs_aggregations(self) -> bool:
        return self.aggregation_hash != self.current_aggregation_hash

    @property
    @abstractmethod
    def current_aggregation_hash(self) -> str:
        pass

    @abstractmethod
    def update_aggregations(self) -> None:
        pass
