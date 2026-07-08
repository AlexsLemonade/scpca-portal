from abc import abstractmethod
from datetime import datetime, timedelta

from django.db import models
from django.db.models import F, QuerySet
from django.utils.timezone import make_aware

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

    def update_loadable_state(self, new_state: LoadableResourceStates) -> None:
        if new_state == LoadableResourceStates.SYNCED:
            type(self).objects.filter(pk=self.pk).update(
                hash=self.current_hash,
                state=new_state,
                updated_at=make_aware(datetime.now()),
                loaded_at=F("updated_at") + timedelta(microseconds=1),
            )
            self.refresh_from_db(fields=["hash", "state", "updated_at", "loaded_at"])
        else:
            self.state = new_state
            self.save()

    @property
    @abstractmethod
    def original_files(self) -> QuerySet[OriginalFile]:
        pass

    @property
    def current_hash(self) -> str:
        original_file_hashes = self.original_files.values_list("hash", flat=True)
        return utils.hash_values(original_file_hashes)
