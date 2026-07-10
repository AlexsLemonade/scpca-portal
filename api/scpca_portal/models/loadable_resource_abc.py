from abc import abstractmethod
from datetime import datetime, timedelta

from django.db import models
from django.db.models import QuerySet
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)


class LoadableResourceABC(TimestampedModel, models.Model):
    class Meta:
        abstract = True

    state = models.TextField(choices=LoadableResourceStates.choices)
    hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)

    def update_loadable_state(self, new_state: LoadableResourceStates) -> None:
        """Updates the state and synchronization tracking fields for a single loadable resource."""
        update_fields = ["state"]
        self.state = new_state
        if new_state == LoadableResourceStates.SYNCED:
            self.hash = self.current_hash
            self.updated_at = make_aware(datetime.now())
            # loaded_at needs to be set after updated_at to ensure aggregations are re-computed
            self.loaded_at = self.updated_at + timedelta(microseconds=1)
            # this is necessary so updated_at is not overwritten by auto_new during save op
            update_fields.extend(["hash", "updated_at", "loaded_at"])
        self.save(update_fields=update_fields)

    @classmethod
    def bulk_update_loadable_state(
        cls, loadable_resources: QuerySet[Self], new_state: LoadableResourceStates
    ) -> None:
        """Performs a highly optimized batch update on a QuerySet of loadable resources."""
        if not loadable_resources.exists():
            return

        if new_state == LoadableResourceStates.SYNCED:
            # This is an optimized approach to grabbing all hash values
            # in order for the row updating to stay at the DB level
            hash_cases = [
                models.When(pk=lr.pk, then=models.Value(lr.current_hash))
                for lr in loadable_resources
            ]

            loadable_resources_pks = [lr.pk for lr in loadable_resources]
            now_timestamp = make_aware(datetime.now())
            # filter explicitly by primary keys rather than updating the original queryset directly.
            # this prevents a race condition where a phantom row matching the original filters
            # is added to the db after hash_cases evaluates, which would cause an invalid state
            # inside the SQL CASE statement during the update.
            cls.objects.filter(pk__in=loadable_resources_pks).update(
                hash=models.Case(*hash_cases, output_field=cls._meta.get_field("hash")),
                state=new_state,
                updated_at=now_timestamp,
                loaded_at=(now_timestamp + timedelta(microseconds=1)),
            )
            # This ensures that the objects' fields have their updated values for downstream use
            for loadable_resource in loadable_resources:
                loadable_resource.refresh_from_db(
                    fields=["hash", "state", "updated_at", "loaded_at"]
                )
        else:
            # As queryset was not opened up, no eager refresh needed as lazy evaluation is expected
            loadable_resources.update(state=new_state)

    @property
    @abstractmethod
    def original_files(self) -> QuerySet[OriginalFile]:
        pass

    @property
    def current_hash(self) -> str:
        original_file_hashes = self.original_files.values_list("hash", flat=True)
        return utils.hash_values(original_file_hashes)
