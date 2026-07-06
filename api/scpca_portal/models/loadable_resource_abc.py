from abc import abstractmethod
from typing import List

from django.db import models
from django.db.models import QuerySet

from typing_extensions import Self

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)


class LoadableResourceABC(models.Model):
    class Meta:
        abstract = True

    state = models.TextField(choices=LoadableResourceStates.choices)
    hash = models.CharField(max_length=32, null=True)
    loaded_at = models.DateTimeField(null=True)

    @property
    def update(self) -> None:
        pass

    @classmethod
    def bulk_update(cls, loadable_resources: List[Self]) -> None:
        pass

    @property
    def update_state(self) -> None:
        pass

    @classmethod
    def bulk_update_state(cls, loadable_resources: List[Self]) -> None:
        pass

    @property
    @abstractmethod
    def original_files(self) -> QuerySet[OriginalFile]:
        pass

    @property
    def current_hash(self) -> str:
        original_file_hashes = self.original_files.values_list("hash", flat=True)
        return utils.hash_values(original_file_hashes)
