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

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="libraries")

    def __str__(self):
        return f"Library {self.scpca_id}"

    @classmethod
    def get_from_dict(cls, data, project):
        data_file_paths = Library.get_data_file_paths(data)
        library = cls(
            data_file_paths=data_file_paths,
            formats=Library.get_formats_from_file_paths(data_file_paths),
            is_multiplexed=data.get("is_multiplexed", False),
            metadata=data,
            modality=Library.get_modality_from_file_paths(data_file_paths),
            project=project,
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
                libraries.append(Library.get_from_dict(library_json, sample.project))

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
        format_extensions_swapped = {v: k for k, v in common.FORMAT_EXTENSIONS.items()}
        formats = set(format_extensions_swapped.get(path.suffix, None) for path in file_paths)
        return list(formats)

    @classmethod
    def get_project_libraries_from_download_config(
        cls, project, download_configuration: Dict
    ):  # -> QuerySet[Self]:
        if download_configuration not in common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS:
            raise ValueError("Invalid download configuration passed. Unable to retrieve libraries.")

        if download_configuration["metadata_only"]:
            return project.libraries.all()

        if download_configuration["includes_merged"]:
            # If the download config requests merged and there is no merged file in the project,
            # return an empty queryset
            if (
                download_configuration["format"] == Library.FileFormats.SINGLE_CELL_EXPERIMENT
                and not project.includes_merged_sce
            ):
                return project.libraries.none()
            elif (
                download_configuration["format"] == Library.FileFormats.ANN_DATA
                and not project.includes_merged_anndata
            ):
                return project.libraries.none()

        libraries_queryset = project.libraries.filter(
            modality=download_configuration["modality"],
            formats__contains=[download_configuration["format"]],
        )

        if download_configuration["excludes_multiplexed"]:
            return libraries_queryset.exclude(is_multiplexed=True)

        return libraries_queryset

    @classmethod
    def get_sample_libraries_from_download_config(
        cls, sample, download_configuration: Dict
    ):  # -> QuerySet[Self]:
        if download_configuration not in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGURATIONS:
            raise ValueError("Invalid download configuration passed. Unable to retrieve libraries.")

        return sample.libraries.filter(
            modality=download_configuration["modality"],
            formats__contains=[download_configuration["format"]],
        )

    @staticmethod
    def get_local_path_from_data_file_path(data_file_path: Path) -> Path:
        return common.INPUT_DATA_PATH / data_file_path

    def get_metadata(self) -> Dict:
        library_metadata = {
            "scpca_library_id": self.scpca_id,
        }

        excluded_metadata_attributes = [
            "scpca_sample_id",
            "has_citeseq",
        ]
        library_metadata.update(
            {
                key: self.metadata[key]
                for key in self.metadata
                if key not in excluded_metadata_attributes
            }
        )

    def get_combined_library_metadata(self) -> List[Dict]:
        return [
            self.project.get_metadata() | sample.get_metadata() | self.get_metadata()
            for sample in self.samples
        ]

    def get_download_config_file_paths(self, download_config: Dict) -> List[Path]:
        omit_suffixes = set(common.FORMAT_EXTENSIONS.values())
        omit_suffixes.remove(common.FORMAT_EXTENSIONS.get(download_config["format"], None))

        if download_config["metadata_only"]:
            omit_suffixes.clear()

        return [
            file_path
            for file_path in [Path(fp) for fp in self.data_file_paths]
            if file_path.suffix not in omit_suffixes
        ]
