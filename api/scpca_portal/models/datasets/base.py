import uuid
from abc import ABC

from django.db import models

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetFormats
from scpca_portal.models.api_token import APIToken
from scpca_portal.models.computed_file import ComputedFile

logger = get_and_configure_logger(__name__)


class DatasetABC(ABC):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-editable
    format = models.TextField(choices=DatasetFormats.choices)  # Required upon creation
    data = models.JSONField(default=dict)
    email = models.EmailField(null=True)
    start = models.BooleanField(default=False)

    # Required upon regeneration
    regenerated_from = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.SET_NULL,
        related_name="regenerated_datasets",
    )

    # Hashes
    data_hash = models.CharField(max_length=32, null=True)
    metadata_hash = models.CharField(max_length=32, null=True)
    readme_hash = models.CharField(max_length=32, null=True)
    combined_hash = models.CharField(max_length=32, null=True)

    # Cached File Attrs
    includes_files_bulk = models.BooleanField(default=False)
    includes_files_cite_seq = models.BooleanField(default=False)
    includes_files_merged = models.BooleanField(default=False)
    includes_files_multiplexed = models.BooleanField(default=False)
    estimated_size_in_bytes = models.BigIntegerField(default=0)

    # Non user-editable - set during processing
    started_at = models.DateTimeField(null=True)
    is_started = models.BooleanField(default=False)
    pending_at = models.DateTimeField(null=True)
    is_pending = models.BooleanField(default=False)
    processing_at = models.DateTimeField(null=True)
    is_processing = models.BooleanField(default=False)
    succeeded_at = models.DateTimeField(null=True)
    is_succeeded = models.BooleanField(default=False)
    failed_at = models.DateTimeField(null=True)
    is_failed = models.BooleanField(default=False)
    failed_reason = models.TextField(null=True)
    expires_at = models.DateTimeField(null=True)
    is_expired = models.BooleanField(default=False)  # Set by cronjob
    terminated_at = models.DateTimeField(null=True)
    is_terminated = models.BooleanField(default=False)
    terminated_reason = models.TextField(null=True)

    computed_file = models.OneToOneField(
        ComputedFile,
        null=True,
        on_delete=models.SET_NULL,
        related_name="dataset",
    )
    token = models.ForeignKey(
        APIToken,
        null=True,
        on_delete=models.SET_NULL,
        related_name="datasets",
    )
    download_tokens = models.ManyToManyField(
        APIToken,
        related_name="downloaded_datasets",
    )
