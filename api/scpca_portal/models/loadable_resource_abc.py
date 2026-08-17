from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Iterable, List

from django.db import models
from django.db.models import QuerySet
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import metadata_parser, s3, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)


class LoadableResourceABC(TimestampedModel):
    class Meta:
        abstract = True

    loaded_state = models.TextField(
        choices=LoadableResourceStates.choices, default=LoadableResourceStates.NEW
    )
    loaded_hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)

    @abstractmethod
    def update_from_dict(self, data: Dict) -> Self:
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
        """
        This property returns all original files associated with the resource
        and its subordinate relations, whether downloadable or not.
        """
        pass

    @property
    def current_loaded_hash(self) -> str:
        loaded_original_file_hashes = self.loaded_original_files.values_list("hash", flat=True)
        return utils.hash_values(loaded_original_file_hashes)

    @classmethod
    @abstractmethod
    def get_all_input_metadata_files(cls) -> QuerySet[OriginalFile]:
        pass

    @classmethod
    def download_model_metadata(cls) -> None:
        s3.download_files(cls.get_all_input_metadata_files())

    @classmethod
    @abstractmethod
    def get_metadata_dicts_by_id(
        cls, *, resources: QuerySet[Self] | None = None
    ) -> Dict[str, Dict]:
        pass

    @classmethod
    def sync_metadata(cls) -> None:
        updatable_resources = cls.objects.filter(
            loaded_state__in=[LoadableResourceStates.NEW, LoadableResourceStates.TAINTED]
        )
        if not updatable_resources.exists():
            return

        metadata_by_id = cls.get_metadata_dicts_by_id(resources=updatable_resources)
        for resource in updatable_resources:
            # TODO: (Tech Debt) scpca_id will either be moved to a Resource base class
            # or assigned as the pk for derived models in the future
            resource.update_from_dict(metadata_by_id[getattr(resource, "scpca_id")])
            resource.update_loaded_state(LoadableResourceStates.SYNCED, save=False)

        fields_to_update = [f.name for f in cls._meta.concrete_fields if not f.primary_key]
        cls.objects.bulk_update(updatable_resources, fields=fields_to_update)

    @staticmethod
    def get_bulk_object_id_tuples() -> list[tuple[str, str, str]]:
        return [
            (bulk_md["scpca_project_id"], bulk_md["scpca_sample_id"], bulk_md["scpca_library_id"])
            for bulk_md in metadata_parser.download_and_load_all_bulk_metadata()
        ]

    @staticmethod
    def get_metadata_id_tuples(
        metadata_dicts: Iterable[Dict],
    ) -> list[tuple[str | None, str | None, str | None]]:
        return [
            (
                bulk_md.get("scpca_project_id"),
                bulk_md.get("scpca_sample_id"),
                bulk_md.get("scpca_library_id"),
            )
            for bulk_md in metadata_dicts
        ]

    @classmethod
    @abstractmethod
    def create_new_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> None:
        pass

    @classmethod
    @abstractmethod
    def remove_deleted_objects(cls) -> None:
        pass

    @staticmethod
    @abstractmethod
    def get_lockfile_filter_kwargs(lockfile_project_ids: List) -> Dict:
        pass

    @classmethod
    def handle_locked_objects(cls) -> None:
        """
        This method handles two independent actions:
        1. Locking resources who's projects are associated with a lockfile in the OF table
        2. Unlocking projects that were previously in a locked state
        but who's project's lockfile has since been removed.

        Unlocked existing projects are moved to a SYCNED state, while
        unlocked new projects are moved to a NEW state.
        """
        lockfile_project_ids = list(
            OriginalFile.objects.filter(is_lockfile=True).values_list("project_id", flat=True)
        )

        unlocked_libraries = cls.objects.filter(loaded_state=LoadableResourceStates.LOCKED).exclude(
            **cls.get_lockfile_filter_kwargs(lockfile_project_ids)
        )
        # existing unlocked libraries should be set to SYNCED
        cls.bulk_update_loaded_state(
            unlocked_libraries.filter(loaded_at__isnull=False), LoadableResourceStates.SYNCED
        )
        # new unlocked libraries should be set to NEW
        cls.bulk_update_loaded_state(
            unlocked_libraries.filter(loaded_at__isnull=True), LoadableResourceStates.NEW
        )

        locked_libraries = cls.objects.filter(
            **cls.get_lockfile_filter_kwargs(lockfile_project_ids)
        )
        cls.bulk_update_loaded_state(locked_libraries, LoadableResourceStates.LOCKED)

    @classmethod
    def taint_modified_objects(cls) -> None:
        tainted_objs = [
            synced_obj
            for synced_obj in cls.objects.filter(loaded_state=LoadableResourceStates.SYNCED)
            if synced_obj.loaded_hash != synced_obj.current_loaded_hash
        ]
        cls.bulk_update_loaded_state(tainted_objs, LoadableResourceStates.TAINTED)

    @classmethod
    @abstractmethod
    def get_model_metadata(cls) -> List[Dict]:
        pass

    @classmethod
    def sync_model(cls) -> None:
        cls.download_model_metadata()
        metadata_dicts_by_id = cls.get_metadata_dicts_by_id()

        cls.create_new_objects(metadata_dicts_by_id)
        cls.remove_deleted_objects()
        cls.handle_locked_objects()
        cls.taint_modified_objects()
