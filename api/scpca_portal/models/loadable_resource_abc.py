from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Iterable

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
        cls, loadable_resources: Iterable[Self], new_loaded_state: LoadableResourceStates
    ) -> Iterable[Self]:
        """Performs a highly optimized batch update on a QuerySet or list of loadable resources."""
        if not loadable_resources:
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

    @classmethod
    @abstractmethod
    def create_new_objects(cls) -> None:
        pass

    @classmethod
    @abstractmethod
    def remove_deleted_objects(cls) -> None:
        pass

    @classmethod
    def handle_locked_objects(cls) -> None:
        # 3 Step Process:
        #   1) query OF table for all present lockfiles
        #      and grab values_list for locked project ids
        #   2) all projects with a loaded_state of LOCKED not in the values_list, set to SYNCED
        #   3) all projects with ids in the values_list, set loaded_state to LOCKED

        # NOTE: We should consider a new state called UNLOCKED, so projects no longer LOCKED
        # can transition to something other than SYNCED.
        # We don't want to transition directly to TAINTED,
        # because the TAINTED transition is dependent on hashing comparison logic,
        # which should live in exclusively in one place (taint_modified_objects).

        # NOTE: To stay consistent with sync_models being dependent solely on the OF table
        # and not the S3 bucket,
        # project lockfiles must be converted to original files and read from the OF table.
        # Currently, the lockfile module reads directly from S3.
        pass

    @classmethod
    def taint_modified_objects(cls) -> None:
        tainted_objs = [
            synced_obj
            for synced_obj in cls.objects.filter(loaded_state=LoadableResourceStates.SYNCED)
            if synced_obj.loaded_hash != synced_obj.current_loaded_hash
        ]
        cls.bulk_update_loaded_state(tainted_objs, LoadableResourceStates.TAINTED)

    @classmethod
    def sync_model(cls) -> None:
        cls.create_new_objects()
        cls.remove_deleted_objects()
        cls.handle_locked_objects()
        cls.taint_modified_objects()
