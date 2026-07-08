from abc import abstractmethod
from datetime import datetime, timedelta

from django.db import models
from django.db.models import F, QuerySet
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
        if new_state == LoadableResourceStates.SYNCED:
            # Executes SQL Update directly on DB, ensuring that loaded_at is set after updated_at,
            # which is important for determining whether aggregations need to be re-computed
            type(self).objects.filter(pk=self.pk).update(
                hash=self.current_hash,
                state=new_state,
                updated_at=make_aware(datetime.now()),
                loaded_at=F("updated_at") + timedelta(microseconds=1),
            )
            # This ensures that the object's fields have their updated values for downstream use
            self.refresh_from_db(fields=["hash", "state", "updated_at", "loaded_at"])
        else:
            self.state = new_state
            self.save()

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
                models.When(
                    pk=loadable_resource.pk, then=models.Value(loadable_resource.current_hash)
                )
                for loadable_resource in loadable_resources
            ]

            loadable_resources.update(
                hash=models.Case(*hash_cases, output_field=cls._meta.get_field("hash")),
                state=new_state,
                updated_at=make_aware(datetime.now()),
                loaded_at=F("updated_at") + timedelta(microseconds=1),
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
