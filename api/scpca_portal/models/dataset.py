import uuid

from django.db import models

from scpca_portal.models import APIToken, ComputedFile
from scpca_portal.models.base import TimestampedModel


class Dataset(TimestampedModel):
    class Meta:
        db_table = "dataset"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    class FileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField(default=dict)
    format = models.TextField(choices=FileFormats.CHOICES, null=True)
    email = models.EmailField(max_length=254, null=True)
    regenerated_from = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.CASCADE,
        related_name="original_dataset",
        help_text="Reference to the original dataset if regenerated.",
    )
    start = models.BooleanField(
        null=True,
        help_text="Indicates if the dataset process has started.",
    )

    token = models.OneToOneField(
        APIToken,
        null=True,
        on_delete=models.CASCADE,
        related_name="dataset_token",
        help_text="Token used to process the dataset.",
    )
    download_tokens = models.ManyToManyField(
        APIToken,
        related_name="dataset_download_tokens",
        help_text="Tokens used to create download.",
    )

    started_at = models.DateTimeField(null=True)
    is_started = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True)
    is_processed = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True)
    is_expired = models.BooleanField(default=False)
    errored_at = models.DateTimeField(null=True)
    is_errored = models.BooleanField(default=False)
    error_message = models.TextField(null=True)

    computed_file = models.OneToOneField(
        ComputedFile,
        null=True,
        on_delete=models.CASCADE,
        related_name="dataset_computed_file",
        help_text="A computed file generated for the dataset.",
    )

    def __str__(self):
        return f"Dataset {self.id}"
