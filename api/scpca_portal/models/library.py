from pathlib import Path
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import utils
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
        return f"Library id {self.scpca_id}"

    @classmethod
    def get_from_dict(cls, data):
        library = cls(
            # Populate and pop temporary fields
            formats=data.pop("formats"),
            modality=data.pop("modality"),
            # Populate calculated fields
            is_multiplexed=("demux_samples" in data),
            # Populate persisted fields
            metadata=data,
            scpca_id=data["scpca_library_id"],
            workflow_version=data["workflow_version"],
        )

        return library

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample) -> None:
        libraries = []
        for library_json in library_jsons:
            if library := Library.objects.filter(scpca_id=library_json["scpca_library_id"]).first():
                library.samples.add(sample)
                library_json.pop("modality", None)
                library_json.pop("formats", None)
            else:
                libraries.append(Library.get_from_dict(library_json))

        Library.objects.bulk_create(libraries)
        sample.libraries.add(*libraries)

    @staticmethod
    def get_file_formats(sample_dir: Path):
        file_formats = []
        if any(sample_dir.glob("*.rds")):
            file_formats.append(Library.FileFormats.SINGLE_CELL_EXPERIMENT)
        if any(sample_dir.glob("*.h5ad")):
            file_formats.append(Library.FileFormats.ANN_DATA)

        return file_formats

    def get_data_file_paths(self) -> List[Path]:
        """
        Retrieves all data file paths on the aws input bucket associated with the Library object
        and returns them as a list
        """
        project_id = self.samples.first().project.scpca_id
        sample_id = (
            self.samples.first().scpca_id
            if self.samples.count() == 1
            else ",".join([sample.scpca_id for sample in self.samples.all()])
        )
        library_id = self.scpca_id
        relative_path = Path(f"{project_id}/{sample_id}/{library_id}")

        data_file_paths = [
            # Final directory in bucket name, which aws inserts at beginning of each returned path,
            # is removed here by way of slicing
            Path().joinpath(*((file_path.parts)[1:]))
            for file_path in utils.list_s3_paths(relative_path)
            if "metadata" not in file_path.name
        ]

        return data_file_paths
