from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common, utils
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
        library = cls(
            formats=Library.get_formats(data["scpca_library_id"]),
            is_multiplexed=data.get("is_multiplexed", False),
            has_cite_seq_data=Library.get_has_cite_seq(data["scpca_library_id"]),
            metadata=data,
            modality=Library.get_modality(data["scpca_library_id"]),
            project=project,
            scpca_id=data["scpca_library_id"],
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

    @staticmethod
    def _get_original_files(library_id: str):
        """Retrieve all original files associated with the passed library id."""
        return OriginalFile.objects.filter(library_id=library_id)

    @property
    def data_file_paths(self):
        return sorted(self.original_files.values_list("s3_key", flat=True))

    @property
    def original_files(self):
        original_files = Library._get_original_files(self.scpca_id)
        if Library.get_modality(self.scpca_id) == Library.Modalities.SINGLE_CELL:
            return original_files.exclude(is_metadata=True)
        return original_files

    @staticmethod
    def get_modality(library_id: str) -> str:
        all_file_paths = utils.convert_to_path_objects(
            OriginalFile.objects.filter(library_id=library_id).values_list("s3_key", flat=True)
        )
        if any(path for path in all_file_paths if "spatial" in path.parts):
            return Library.Modalities.SPATIAL
        return Library.Modalities.SINGLE_CELL

    @staticmethod
    def get_formats(library_id: str) -> List[str]:
        if Library.get_modality(library_id) is Library.Modalities.SPATIAL:
            return [Library.FileFormats.SINGLE_CELL_EXPERIMENT]

        all_file_paths = utils.convert_to_path_objects(
            OriginalFile.objects.filter(library_id=library_id).values_list("s3_key", flat=True)
        )

        extensions_format = {v: k for k, v in common.FORMAT_EXTENSIONS.items()}
        formats = set(
            extensions_format[path.suffix]
            for path in all_file_paths
            if path.suffix in extensions_format
        )
        return sorted(list(formats))

    @staticmethod
    def get_has_cite_seq(library_id: str) -> bool:
        all_file_paths = utils.convert_to_path_objects(
            OriginalFile.objects.filter(library_id=library_id).values_list("s3_key", flat=True)
        )
        return any(fp for fp in all_file_paths if "_adt." in fp.name)

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

    def get_download_config_file_paths(self, download_config: Dict) -> List[Path]:
        """
        Return all of a library's file paths that are suitable for the passed download config.
        """

        if download_config.get("metadata_only", False):
            return []

        omit_suffixes = set(common.FORMAT_EXTENSIONS.values())

        if not download_config.get("includes_merged", False):
            requested_suffix = common.FORMAT_EXTENSIONS.get(download_config["format"])
            omit_suffixes.remove(requested_suffix)

        return [
            file_path
            for file_path in [Path(fp) for fp in self.data_file_paths]
            if file_path.suffix not in omit_suffixes
        ]

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
