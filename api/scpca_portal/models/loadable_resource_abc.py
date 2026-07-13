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


class LoadableResourceABC(TimestampedModel):
    class Meta:
        abstract = True

    state = models.TextField(choices=LoadableResourceStates.choices)
    hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)

    def update_loadable_state(self, new_state: LoadableResourceStates, save: bool = True) -> Self:
        """Updates the state and synchronization tracking fields for a single loadable resource."""
        self.state = new_state
        self.updated_at = make_aware(datetime.now())
        # this is necessary so updated_at is not overwritten by auto_new during save op,
        # allowing for us to set loaded_at after updated_at (if need be)
        fields_to_update = ["state", "updated_at"]

        if new_state == LoadableResourceStates.SYNCED:
            self.hash = self.current_hash
            # loaded_at needs to be set after updated_at to ensure aggregations are re-computed
            self.loaded_at = self.updated_at + timedelta(microseconds=1)
            fields_to_update.extend(["hash", "loaded_at"])

        if save:
            self.save(update_fields=fields_to_update)

        return self

    @classmethod
    def bulk_update_loadable_state(
        cls, loadable_resources: QuerySet[Self], new_state: LoadableResourceStates
    ) -> QuerySet[Self]:
        """Performs a highly optimized batch update on a QuerySet of loadable resources."""
        if not loadable_resources.exists():
            return loadable_resources

        for loadable_resource in loadable_resources:
            loadable_resource.update_loadable_state(new_state=new_state, save=False)

        fields_to_update = ["state", "updated_at"]
        if new_state == LoadableResourceStates.SYNCED:
            fields_to_update.extend(["hash", "loaded_at"])

        cls.objects.bulk_update(loadable_resources, fields=fields_to_update)

        return loadable_resources

    @property
    @abstractmethod
    def original_files(self) -> QuerySet[OriginalFile]:
        pass

    @property
    def current_hash(self) -> str:
        original_file_hashes = self.original_files.values_list("hash", flat=True)
        return utils.hash_values(original_file_hashes)
