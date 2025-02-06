from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.original_file import OriginalFile


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
    has_cite_seq_data = models.BooleanField(default=False)
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
        library_id = data["scpca_library_id"]
        original_files = OriginalFile.downloadable_objects.filter(library_id=library_id)

        modality = ""
        if original_files.filter(is_single_cell=True).exists():
            modality = Library.Modalities.SINGLE_CELL
        elif original_files.filter(is_spatial=True).exists():
            modality = Library.Modalities.SPATIAL

        formats = []
        if original_files.filter(is_single_cell_experiment=True).exists():
            formats.append(Library.FileFormats.SINGLE_CELL_EXPERIMENT)
        if original_files.filter(is_anndata=True).exists():
            formats.append(Library.FileFormats.ANN_DATA)

        library = cls(
            formats=sorted(formats),
            is_multiplexed=data.get("is_multiplexed", False),
            has_cite_seq_data=original_files.filter(is_cite_seq=True).exists(),
            metadata=data,
            modality=modality,
            project=project,
            scpca_id=library_id,
            workflow_version=data["workflow_version"],
        )

        return library

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample) -> None:
        libraries = []
        for library_json in library_jsons:
            library_id = library_json["scpca_library_id"]
            if existing_library := Library.objects.filter(scpca_id=library_id).first():
                sample.libraries.add(existing_library)
            else:
                # TODO: remove when scpca_project_id is in source json
                library_json["scpca_project_id"] = sample.project.scpca_id
                libraries.append(Library.get_from_dict(library_json, sample.project))

        Library.objects.bulk_create(libraries)
        sample.libraries.add(*libraries)

    @property
    def original_files(self):
        return OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)

    @property
    def original_file_paths(self) -> List[str]:
        return sorted(self.original_files.values_list("s3_key", flat=True))

    @staticmethod
    def get_local_path_from_data_file_path(data_file_path: Path) -> Path:
        return settings.INPUT_DATA_PATH / data_file_path

    def get_metadata(self, demux_cell_count_estimate_id) -> Dict:
        excluded_metadata_attributes = {
            "scpca_sample_id",
            "has_citeseq",
            "sample_cell_estimates",
        }
        library_metadata = {
            key: value
            for key, value in self.metadata.items()
            if key not in excluded_metadata_attributes
        }

        if self.is_multiplexed:
            library_metadata["demux_cell_count_estimate"] = self.metadata["sample_cell_estimates"][
                demux_cell_count_estimate_id
            ]

        return library_metadata

    def get_combined_library_metadata(self) -> List[Dict]:
        return [
            self.project.get_metadata() | sample.get_metadata() | self.get_metadata(sample.scpca_id)
            for sample in self.samples.all()
        ]

    def get_original_files_by_download_config(self, download_config: Dict):
        """
        Return all of a library's file paths that are suitable for the passed download config.
        """
        if download_config.get("metadata_only", False):
            return OriginalFile.objects.none()

        original_files = OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)
        if not download_config.get("includes_merged", False):
            if download_config["format"] == Library.FileFormats.ANN_DATA:
                return original_files.exclude(is_single_cell_experiment=True)
            if download_config["format"] == Library.FileFormats.SINGLE_CELL_EXPERIMENT:
                return original_files.exclude(is_anndata=True)

        return original_files.exclude(is_single_cell_experiment=True).exclude(is_anndata=True)

    @staticmethod
    def get_local_file_path(file_path: Path):
        return settings.INPUT_DATA_PATH / file_path

    @staticmethod
    def get_zip_file_path(file_path: Path, download_config: Dict) -> Path:
        path_parts = [Path(path) for path in file_path.parts]

        # Project output paths are relative to project directory
        if download_config in common.PROJECT_DOWNLOAD_CONFIGS.values():
            output_path = file_path.relative_to(path_parts[0])
        # Sample output paths are relative to project and sample directories
        else:
            output_path = file_path.relative_to(path_parts[0] / path_parts[1])

        # Transform merged and bulk project data files to no longer be nested in a merged directory
        if file_path.parent.name in ["bulk", "merged"]:
            output_path = file_path.relative_to(path_parts[0] / path_parts[1])
        # Nest sample reports into individual_reports directory in merged download
        # The merged summmary html file should not go into this directory
        elif download_config.get("includes_merged", False) and output_path.suffix == ".html":
            output_path = Path("individual_reports") / output_path

        # Comma separated lists of multiplexed samples should become underscore separated
        return Path(str(output_path).replace(",", "_"))

    @staticmethod
    def get_libraries_metadata(libraries) -> List[Dict]:
        return [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]

    @staticmethod
    def get_file_paths(libraries, download_config):
        """
        Return file paths associated with the libraries according to the passed download_config.
        Files are then downloaded and included in computed files.
        """
        library_file_paths = [
            Path(of.s3_key)
            for lib in libraries
            for of in lib.get_original_files_by_download_config(download_config)
        ]

        if download_config in common.PROJECT_DOWNLOAD_CONFIGS.values():
            project = libraries.first().project
            project_file_paths = [
                Path(of.s3_key)
                for of in project.get_original_files_by_download_config(download_config)
            ]
            return project_file_paths + library_file_paths

        return library_file_paths
