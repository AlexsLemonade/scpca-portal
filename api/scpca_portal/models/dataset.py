import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from django.conf import settings
from django.db import models

from typing_extensions import Self

from scpca_portal import ccdl_datasets, common, metadata_file, readme_file, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import (
    CCDLDatasetNames,
    DatasetDataProjectConfig,
    DatasetFormats,
    Modalities,
)
from scpca_portal.models.api_token import APIToken
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.library import Library
from scpca_portal.models.original_file import OriginalFile
from scpca_portal.models.project import Project
from scpca_portal.models.sample import Sample

logger = get_and_configure_logger(__name__)


class Dataset(TimestampedModel):
    class Meta:
        db_table = "datasets"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-editable
    data = models.JSONField(default=dict)
    email = models.EmailField(null=True)
    start = models.BooleanField(default=False)

    # Format or regenerated_from is required at the time of creation
    format = models.TextField(choices=DatasetFormats.choices)
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

    # Internally generated datasets
    is_ccdl = models.BooleanField(default=False)
    ccdl_name = models.TextField(choices=CCDLDatasetNames.choices, null=True)
    ccdl_project_id = models.TextField(null=True)

    # Non user-editable - set during processing
    started_at = models.DateTimeField(null=True)
    is_started = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True)
    is_processed = models.BooleanField(default=False)
    errored_at = models.DateTimeField(null=True)
    is_errored = models.BooleanField(default=False)
    error_message = models.TextField(null=True)
    expires_at = models.DateTimeField(null=True)
    is_expired = models.BooleanField(default=False)  # Set by cronjob

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

    def __str__(self):
        return f"Dataset {self.id}"

    @classmethod
    def get_or_find_ccdl_dataset(
        cls, ccdl_name: CCDLDatasetNames, project_id: str | None = None
    ) -> tuple[Self, bool]:
        if dataset := cls.objects.filter(
            is_ccdl=True, ccdl_name=ccdl_name, ccdl_project_id=project_id
        ).first():
            return dataset, True

        dataset = cls(is_ccdl=True, ccdl_name=ccdl_name, ccdl_project_id=project_id)
        dataset.format = dataset.ccdl_type["format"]
        dataset.data = dataset.get_ccdl_data()
        dataset.data_hash = dataset.current_data_hash
        dataset.metadata_hash = dataset.current_metadata_hash
        dataset.readme_hash = dataset.current_readme_hash
        return dataset, False

    def get_ccdl_data(self) -> Dict:
        if not self.is_ccdl:
            raise ValueError("Invalid Dataset: Dataset must be CCDL.")

        projects = Project.objects.all()
        if self.ccdl_project_id:
            projects = projects.filter(scpca_id=self.ccdl_project_id)

        data = {}
        for project in projects:
            samples = project.samples.all()
            if self.ccdl_type.get("excludes_multiplexed"):
                samples = samples.filter(has_multiplexed_data=False)

            if modality := self.ccdl_type.get("modality"):
                samples = samples.filter(libraries__modality=modality)

            single_cell_samples = samples.filter(libraries__modality=Modalities.SINGLE_CELL)
            spatial_samples = samples.filter(libraries__modality=Modalities.SPATIAL)

            data[project.scpca_id] = {
                "merge_single_cell": self.ccdl_type.get("includes_merged"),
                "includes_bulk": True,
                Modalities.SINGLE_CELL: list(
                    single_cell_samples.values_list("scpca_id", flat=True)
                ),
                Modalities.SPATIAL: list(spatial_samples.values_list("scpca_id", flat=True)),
            }

        return data

    def get_samples(self, project_id: str, modality: Modalities) -> Iterable[Sample]:
        """
        Takes project's scpca_id and a modality.
        Returns Sample instances defined in data attribute.
        """
        if sample_ids := self.data.get(project_id, {}).get(modality, []):
            return Sample.objects.filter(scpca_id__in=sample_ids).order_by("scpca_id")
        return Sample.objects.none()

    def get_sample_libraries(self, project_id: str, modality: Modalities) -> Iterable[Library]:
        return Library.objects.filter(samples__in=self.get_samples(project_id, modality)).distinct()

    @property
    def is_hash_changed(self) -> bool:
        """
        Determines whether or not a computed file should be generated for the instance dataset.
        Files should be processed for new datasets,
        or for datasets where at least one hash attribute has changed.
        """
        return self.combined_hash != self.current_combined_hash

    @property
    def projects(self) -> Iterable[Project]:
        """Returns all Project instances associated with the Dataset."""
        if project_ids := self.data.keys():
            return Project.objects.filter(scpca_id__in=project_ids).order_by("scpca_id")
        return Project.objects.none()

    @property
    def libraries(self) -> Iterable[Library]:
        """Returns all of a Dataset's library, based on Data and Format attrs."""
        dataset_libraries = Library.objects.none()

        for project_config in self.data.values():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]:
                for sample in Sample.objects.filter(scpca_id__in=project_config[modality]):
                    sample_libraries = sample.libraries.filter(modality=modality)
                    if self.format != DatasetFormats.METADATA:
                        sample_libraries.filter(formats__contains=[self.format])
                    dataset_libraries |= sample_libraries

        return dataset_libraries

    @property
    def ccdl_type(self) -> Dict:
        return ccdl_datasets.TYPES.get(self.ccdl_name, {})

    @property
    def is_data_valid(self) -> bool:
        """Determines if the Dataset's Data attr is valid."""
        data_validator = DataValidator(self.data)
        return data_validator.is_valid

    @property
    def original_files(self) -> Iterable[OriginalFile]:
        """Returns all of a Dataset's associated OriginalFiles."""
        files = OriginalFile.objects.none()
        for project_id, project_config in self.data.items():
            # add spatial files
            files |= OriginalFile.downloadable_objects.filter(
                project_id=project_id,
                is_spatial=True,
                sample_ids__overlap=project_config["SPATIAL"],
            )

            # add single-cell supplementary
            files |= OriginalFile.downloadable_objects.filter(
                project_id=project_id,
                is_single_cell=True,
                is_supplementary=True,
                sample_ids__overlap=project_config["SINGLE_CELL"],
            )

            if project_config["merge_single_cell"]:
                merged_files = OriginalFile.downloadable_objects.filter(
                    project_id=project_id, is_merged=True
                )
                files |= merged_files.filter(formats__contains=[self.format])
                files |= merged_files.filter(is_supplementary=True)
            else:
                files |= OriginalFile.downloadable_objects.filter(
                    project_id=project_id,
                    is_single_cell=True,
                    formats__contains=[self.format],
                    sample_ids__overlap=project_config["SINGLE_CELL"],
                )
            if project_config["includes_bulk"]:
                files |= OriginalFile.downloadable_objects.filter(
                    project_id=project_id, is_bulk=True
                )

        return files

    @property
    def original_file_paths(self) -> Set[Path]:
        return {Path(of.s3_key) for of in self.original_files}

    @property
    def original_file_local_paths(self) -> Set[Path]:
        return {settings.INPUT_DATA_PATH / of.s3_key for of in self.original_files}

    @property
    def original_file_zip_paths(self) -> Set[Path]:
        original_file_zip_paths = set()

        original_files = self.original_files
        for project_id, project_config in self.data.items():
            original_file_zip_paths_project = set()
            for original_file in original_files.filter(project_id=project_id):
                # Project output paths are relative to project directory
                output_path = original_file.s3_key_path.relative_to(
                    Path(original_file.s3_key_info.project_id_part)
                )

                if original_file.is_merged:
                    parent_dir = Path(f"{original_file.project_id}_single-cell_merged")
                    original_file_zip_paths_project.add(
                        parent_dir / output_path.relative_to(common.MERGED_INPUT_DIR)
                    )
                # Nest sample reports into individual_reports directory in merged folder
                # The merged summmary html file should not go into this directory
                elif project_config["merge_single_cell"] and original_file.is_supplementary:
                    parent_dir = Path(f"{original_file.project_id}_single-cell_merged")
                    original_file_zip_paths_project.add(
                        parent_dir / Path(common.MERGED_REPORTS_PREFEX_DIR) / output_path
                    )
                elif original_file.is_bulk:
                    parent_dir = Path(f"{original_file.project_id}_bulk_rna")
                    original_file_zip_paths_project.add(
                        parent_dir / output_path.relative_to(common.BULK_INPUT_DIR)
                    )
                else:
                    modality = (
                        Modalities.SINGLE_CELL.value
                        if original_file.is_single_cell
                        else Modalities.SPATIAL.value
                    )
                    formatted_modality = modality.lower().replace("_", "-")
                    parent_dir = Path(f"{original_file.project_id}_{formatted_modality}")
                    original_file_zip_paths_project.add(parent_dir / output_path)

            if (
                self.get_samples(project_id, Modalities.SINGLE_CELL)
                .filter(has_multiplexed_data=True)
                .exists()
            ):
                original_file_zip_paths_project = {
                    utils.path_replace(
                        zip_file_path,
                        common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER,
                        common.MULTIPLEXED_SAMPLES_OUTPUT_DELIMETER,
                    )
                    for zip_file_path in original_file_zip_paths_project
                }
            original_file_zip_paths.update(original_file_zip_paths_project)

        return original_file_zip_paths

    @property
    def metadata_file_map(self) -> Dict[str, str]:
        metadata_file_map = {}
        for project_id, project_config in self.data.items():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]:
                if not project_config[modality.value]:
                    continue

                metadata_path = self.get_metadata_file_path(project_id, modality)
                metadata_contents = self.get_metadata_file_contents(
                    self.get_sample_libraries(project_id, modality)
                )
                metadata_file_map[metadata_path] = metadata_contents

        return metadata_file_map

    def get_metadata_file_path(self, project_id: str, modality: Modalities) -> Path:
        """Return metadata file path, modality name inside of project_modality directory."""
        modality_formatted = modality.value.lower().replace("_", "-")
        metadata_file_name = f"{modality_formatted}_metadata.tsv"

        if self.data.get(project_id, {}).get("merge_single_cell", False):
            modality_formatted += "_merged"
        metadata_dir = f"{project_id}_{modality_formatted}"
        return Path(metadata_dir) / Path(metadata_file_name)

    def get_metadata_file_contents(self, libraries: Iterable[Library]) -> str:
        libraries_metadata = Library.get_libraries_metadata(libraries)
        return metadata_file.get_file_contents(libraries_metadata)

    @property
    def readme_file_contents(self) -> str:
        return readme_file.get_file_contents_dataset(self)

    @property
    def current_data_hash(self) -> str:
        """Computes and returns the current data hash."""
        sorted_original_file_hashes = self.original_files.order_by("s3_key").values_list(
            "hash", flat=True
        )
        concat_hash = "".join(sorted_original_file_hashes)
        concat_hash_bytes = concat_hash.encode("utf-8")
        return hashlib.md5(concat_hash_bytes).hexdigest()

    @property
    def current_metadata_hash(self) -> str:
        """Computes and returns the current metadata hash."""
        all_metadata_file_contents = "".join(sorted(self.metadata_file_map.values()))
        all_metadata_file_contents_bytes = all_metadata_file_contents.encode("utf-8")
        return hashlib.md5(all_metadata_file_contents_bytes).hexdigest()

    @property
    def current_readme_hash(self) -> str:
        """Computes and returns the current readme hash."""
        # the first line in the readme file contains the current date
        # we must remove this before hashing
        readme_file_contents = self.readme_file_contents.split("\n", 1)[1].strip()
        readme_file_contents_bytes = readme_file_contents.encode("utf-8")
        return hashlib.md5(readme_file_contents_bytes).hexdigest()

    @property
    def combined_hash(self) -> str:
        """
        Combines, computes and returns the combined cached data, metadata and readme hashes.
        """
        concat_hash = self.data_hash + self.metadata_hash + self.readme_hash
        return hashlib.md5(concat_hash.encode("utf-8")).hexdigest()

    @property
    def current_combined_hash(self) -> str:
        """
        Combines, computes and returns the combined current data, metadata and readme hashes.
        """
        concat_hash = self.current_data_hash + self.current_metadata_hash + self.current_readme_hash
        return hashlib.md5(concat_hash.encode("utf-8")).hexdigest()

    @property
    def valid_ccdl_dataset(self) -> bool:
        if not self.libraries:
            return False

        return self.projects.filter(**self.ccdl_type.get("constraints", {}))

    @property
    def computed_file_name(self) -> Path:
        return Path(f"{self.pk}.zip")

    @property
    def computed_file_local_path(self) -> Path:
        return settings.OUTPUT_DATA_PATH / self.computed_file_name

    @property
    def spatial_projects(self) -> Iterable[Project]:
        if self.format != DatasetFormats.SINGLE_CELL_EXPERIMENT:
            return Project.objects.none()

        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(Modalities.SPATIAL, [])
        ]:
            return self.projects.filter(scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def single_cell_projects(self) -> Iterable[Project]:
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(Modalities.SINGLE_CELL)
        ]:
            return Project.objects.filter(scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def bulk_single_cell_projects(self) -> Iterable[Project]:
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(DatasetDataProjectConfig.INCLUDES_BULK)
        ]:
            return Project.objects.filter(scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def cite_seq_projects(self) -> Iterable[Project]:
        return self.projects.filter(has_cite_seq_data=True)


class DataValidator:
    def __init__(self, data: Dict[str, Dict]) -> None:
        self.data: Dict[str, Dict[str, Any]] = data

    @property
    def is_valid(self) -> bool:
        return all(self.validate_project(project_id) for project_id in self.data.keys())

    @property
    def valid_projects(self) -> List[str]:
        return [project_id for project_id in self.data.keys() if self.validate_project(project_id)]

    @property
    def invalid_projects(self) -> List[str]:
        return [
            project_id for project_id in self.data.keys() if not self.validate_project(project_id)
        ]

    def validate_project(self, project_id: str) -> bool:
        if not self._validate_project_id(project_id):
            return False

        if not self._validate_merge_single_cell(project_id):
            return False

        if not self._validate_includes_bulk(project_id):
            return False

        if not self._validate_single_cell(project_id):
            return False

        if not self._validate_spatial(project_id):
            return False

        return True

    def _validate_project_id(self, project_id):
        return self._validate_id(project_id, common.PROJECT_ID_PREFIX)

    def _validate_id(self, id: str, prefix: str) -> bool:
        if not isinstance(id, str):
            return False

        if not id.startswith(prefix):
            return False

        id_number = id.removeprefix(prefix)
        return len(id_number) == 6 and id_number.isdigit()

    def _validate_merge_single_cell(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.MERGE_SINGLE_CELL):
            return isinstance(value, bool)

        return True

    def _validate_includes_bulk(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.INCLUDES_BULK):
            return isinstance(value, bool)

        return True

    def _validate_single_cell(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.SINGLE_CELL):
            return self._validate_modality(value)

        return True

    def _validate_spatial(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.SPATIAL):
            return self._validate_modality(value)

        return True

    def _validate_modality(self, modality_sample_ids: List) -> bool:
        if not isinstance(modality_sample_ids, list):
            return False

        for sample_id in modality_sample_ids:
            if not self._validate_id(sample_id, common.SAMPLE_ID_PREFIX):
                return False

        return True
