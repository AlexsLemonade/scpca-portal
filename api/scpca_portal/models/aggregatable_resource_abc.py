from abc import abstractmethod
from typing import Self

from django.db import models
from django.db.models import QuerySet

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class AggregatableResourceABC(TimestampedModel):
    class Meta:
        abstract = True

    aggregation_hash = models.CharField(max_length=32, null=True)

    @classmethod
    def sync_aggregations(cls, resources: QuerySet[Self]) -> None:
        aggregating_resources = [resource for resource in resources if resource.needs_aggregations]

        for aggregating_resource in aggregating_resources:
            aggregating_resource.update_aggregations()
            aggregating_resource.aggregation_hash = aggregating_resource.current_aggregation_hash

        fields_to_update = [f.name for f in cls._meta.concrete_fields if not f.primary_key]
        cls.objects.bulk_update(aggregating_resources, fields=fields_to_update)

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
