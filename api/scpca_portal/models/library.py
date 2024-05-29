from pathlib import Path
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal.models.base import TimestampedModel


class Library(TimestampedModel):
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

    formats = ArrayField(models.TextField(choices=FileFormats.CHOICES), default=list)
    is_multiplexed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    modality = models.TextField(choices=Modalities.CHOICES)
    scpca_id = models.TextField(unique=True)
    workflow_version = models.TextField()

    @classmethod
    def get_from_dict(cls, data, formats):
        library = cls(
            formats=formats,
            is_multiplexed=("demux_samples" in data),
            metadata=data,
            modality=(
                Library.Modalities.SINGLE_CELL
                if "filtered_cell_count" in data
                else Library.Modalities.SPATIAL
            ),
            scpca_id=data["scpca_library_id"],
            workflow_version=data["workflow_version"],
        )

        return library

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample, sample_dir: Path) -> None:
        libraries = []
        for library_json in library_jsons:
            formats = []
            if "filtered_cell_count" in library_json:
                if any(sample_dir.glob("*.rds")):
                    formats.append(Library.FileFormats.SINGLE_CELL_EXPERIMENT)
                if any(sample_dir.glob("*.h5ad")):
                    formats.append(Library.FileFormats.ANN_DATA)
            else:
                formats.append(Library.FileFormats.SINGLE_CELL_EXPERIMENT)

            libraries.append(Library.get_from_dict(library_json, formats))

        Library.objects.bulk_create(libraries)
        sample.libraries.add(*libraries)
