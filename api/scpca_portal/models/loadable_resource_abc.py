from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List

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

    loaded_state = models.TextField(choices=LoadableResourceStates.choices)
    loaded_hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)

    @classmethod
    @abstractmethod
    # args and kwargs enable overloading so Sample and Library can pass a project obj
    def get_from_dict(cls, data: Dict, *args: Any, **kwargs: Any) -> Self:
        pass

    @abstractmethod
    def update_from_dict(self, data: Dict) -> Self:
        pass

    @classmethod
    @abstractmethod
    def get_loaded_state_metadata_dicts_by_id(
        cls, loaded_states: List[LoadableResourceStates] = []
    ) -> Dict[str, Dict]:
        pass

    @classmethod
    def sync_metadata(cls) -> None:
        updatable_resources = list(
            cls.objects.filter(
                loaded_state__in=[LoadableResourceStates.NEW, LoadableResourceStates.TAINTED]
            )
        )
        if not updatable_resources:
            return

        metadata_by_id = cls.get_loaded_state_metadata_dicts_by_id(
            loaded_states=[LoadableResourceStates.NEW, LoadableResourceStates.TAINTED]
        )
        for resource in updatable_resources:
            resource.update_from_dict(metadata_by_id[getattr(resource, "scpca_id")])
            resource.update_loaded_state(LoadableResourceStates.SYNCED, save=False)

        fields_to_update = [f.name for f in cls._meta.concrete_fields if not f.primary_key]
        cls.objects.bulk_update(updatable_resources, fields=fields_to_update)

    @classmethod
    # not defined as an abstractmethod because Library has no aggregations
    def sync_aggregations(cls) -> None:
        pass

    def update_loaded_state(
        self, new_loaded_state: LoadableResourceStates, save: bool = True
    ) -> Self:
        """Updates the state and synchronization tracking fields for a single loadable resource."""
        self.loaded_state = new_loaded_state
        self.updated_at = make_aware(datetime.now())
        # this is necessary so updated_at is not overwritten by auto_new during save op,
        # allowing for us to set loaded_at after updated_at (if need be)
        fields_to_update = ["loaded_state", "updated_at"]

        if new_loaded_state == LoadableResourceStates.SYNCED:
            self.loaded_hash = self.current_loaded_hash
            # loaded_at needs to be set after updated_at to ensure aggregations are re-computed
            self.loaded_at = self.updated_at + timedelta(microseconds=1)
            fields_to_update.extend(["loaded_hash", "loaded_at"])

        if save:
            self.save(update_fields=fields_to_update)

        return self

    @classmethod
    def bulk_update_loaded_state(
        cls, loadable_resources: QuerySet[Self], new_loaded_state: LoadableResourceStates
    ) -> QuerySet[Self]:
        """Performs a highly optimized batch update on a QuerySet of loadable resources."""
        if not loadable_resources.exists():
            return loadable_resources

        for loadable_resource in loadable_resources:
            loadable_resource.update_loaded_state(new_loaded_state=new_loaded_state, save=False)

        fields_to_update = ["loaded_state", "updated_at"]
        if new_loaded_state == LoadableResourceStates.SYNCED:
            fields_to_update.extend(["loaded_hash", "loaded_at"])

        cls.objects.bulk_update(loadable_resources, fields=fields_to_update)

        return loadable_resources

    @property
    @abstractmethod
    def loaded_original_files(self) -> QuerySet[OriginalFile]:
        pass

    @property
    def current_loaded_hash(self) -> str:
        loaded_original_file_hashes = self.loaded_original_files.values_list("hash", flat=True)
        return utils.hash_values(loaded_original_file_hashes)
