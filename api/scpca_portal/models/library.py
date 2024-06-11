from pathlib import Path
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common, utils
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

    data_file_paths = ArrayField(models.TextField(), default=list)
    formats = ArrayField(models.TextField(choices=FileFormats.CHOICES), default=list)
    is_multiplexed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    modality = models.TextField(choices=Modalities.CHOICES)
    scpca_id = models.TextField(unique=True)
    workflow_version = models.TextField()

    def __str__(self):
        return f"Library {self.scpca_id}"

    @classmethod
    def get_from_dict(cls, data):
        data_file_paths = Library.get_data_file_paths(data)
        library = cls(
            data_file_paths=data_file_paths,
            formats=Library.get_formats_from_file_paths(data_file_paths),
            is_multiplexed=("demux_samples" in data),
            metadata=data,
            modality=Library.get_modality_from_file_paths(data_file_paths),
            scpca_id=data["scpca_library_id"],
            workflow_version=data["workflow_version"],
        )

        return library

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample) -> None:
        libraries = []
        for library_json in library_jsons:
            if not Library.objects.filter(scpca_id=library_json["scpca_library_id"]).exists():
                # TODO: remove when scpca_project_id is in source json
                library_json["scpca_project_id"] = sample.project.scpca_id
                libraries.append(Library.get_from_dict(library_json))

        Library.objects.bulk_create(libraries)
        sample.libraries.add(*libraries)

    @classmethod
    def get_data_file_paths(cls, data) -> List[Path]:
        """
        Retrieves all data file paths on the aws input bucket associated
        with the inputted Library object metadata dict, and returns them as a list.
        """
        # TODO: Pop property for now until attribute added to source json
        project_id = data.pop("scpca_project_id")
        sample_id = data.get("scpca_sample_id")
        library_id = data.get("scpca_library_id")
        relative_path = Path(f"{project_id}/{sample_id}/{library_id}")

        data_file_paths = [
            file_path
            for file_path in utils.list_s3_paths(relative_path)
            if "metadata" not in file_path.name
        ]

        return data_file_paths

    @classmethod
    def get_modality_from_file_paths(cls, file_paths: List[Path]) -> str:
        if any(path for path in file_paths if "spatial" in path.name):
            return Library.Modalities.SPATIAL
        return Library.Modalities.SINGLE_CELL

    @classmethod
    def get_formats_from_file_paths(cls, file_paths: List[Path]) -> List[str]:
        formats = []
        if any(path for path in file_paths if common.SCE_EXT == path.suffix):
            formats.append(Library.FileFormats.SINGLE_CELL_EXPERIMENT)
        if any(path for path in file_paths if common.ANNDATA_EXT == path.suffix):
            formats.append(Library.FileFormats.ANN_DATA)
        return formats
