from django.db import models

from scpca_portal import common
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.sample import Sample


class Library(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "libraries"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    class FileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        )

    class Modalities:
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    dir_path = models.FilePathField(path=common.INPUT_DATA_PATH, recursive=True, allow_folders=True)
    format = models.TextField(choices=FileFormats.CHOICES)
    is_multiplexed = models.BooleanField(default=False)
    modality = models.TextField(choices=Modalities.CHOICES)
    scpca_id = models.TextField(unique=True)
    seq_unit = models.TextField(null=True)
    technology = models.TextField(null=True)

    filtered_cell_count = models.IntegerField(null=True)
    multiplexed_cell_count_estimate = models.IntegerField(null=True)

    samples = models.ManyToManyField(Sample)
