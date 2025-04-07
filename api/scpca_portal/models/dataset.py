import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from django.db import models

from typing_extensions import Self

from scpca_portal import ccdl_datasets, common, metadata_file, readme_file
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
        cls, ccdl_name, project_id: str | None = None
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

            single_cell_samples = samples.filter(libraries__modality=Modalities.SINGLE_CELL.name)
            spatial_samples = samples.filter(libraries__modality=Modalities.SPATIAL.name)

            data[project.scpca_id] = {
                "merge_single_cell": self.ccdl_type.get("includes_merged"),
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: list(
                    single_cell_samples.values_list("scpca_id", flat=True)
                ),
                Modalities.SPATIAL.name: list(spatial_samples.values_list("scpca_id", flat=True)),
            }

        return data

    def should_process(self) -> bool:
        """
        Determines whether or not a computed file should be generated for the instance dataset.
        Files should be processed for new datasets,
        or for datasets where at least one hash attribute has changed.
        """
        cached_combined_hash = Dataset.get_combined_hash(
            self.data_hash, self.metadata_hash, self.readme_hash
        )
        current_combined_hash = Dataset.get_combined_hash(
            self.current_data_hash, self.current_metadata_hash, self.current_readme_hash
        )
        return cached_combined_hash != current_combined_hash

    @property
    def libraries(self) -> Library:
        libraries = Library.objects.none()

        for project_config in self.data.values():
            for modality in [Modalities.SINGLE_CELL.name, Modalities.SPATIAL.name]:
                for sample in Sample.objects.filter(scpca_id__in=project_config[modality]):
                    libraries |= sample.libraries.filter(
                        modality=modality, formats__contains=[self.format]
                    )

        return libraries

    @property
    def ccdl_type(self) -> Dict:
        return ccdl_datasets.TYPES.get(self.ccdl_name)

    @property
    def is_data_valid(self) -> bool:
        data_validator = DataValidator(self.data)
        return data_validator.is_valid

    @property
    def original_files(self) -> Iterable[OriginalFile]:
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
    def metadata_file_contents(self) -> str:
        libraries_metadata = Library.get_libraries_metadata(self.libraries)
        return metadata_file.get_file_contents(libraries_metadata)

    @property
    def readme_file_contents(self) -> str:
        return readme_file.get_file_contents(
            self.ccdl_type, Project.objects.filter(scpca_id__in=self.data.keys())
        )

    @property
    def current_data_hash(self) -> str:
        sorted_original_file_hashes = self.original_files.order_by("s3_key").values_list(
            "hash", flat=True
        )
        concat_hash = "".join(sorted_original_file_hashes)
        concat_hash_bytes = concat_hash.encode("utf-8")
        return hashlib.md5(concat_hash_bytes).hexdigest()

    @property
    def current_metadata_hash(self) -> str:
        metadata_file_contents_bytes = self.metadata_file_contents.encode("utf-8")
        return hashlib.md5(metadata_file_contents_bytes).hexdigest()

    @property
    def current_readme_hash(self) -> str:
        ##########
        # Return 1 until readme_file.get_file_contents is refactored to handle ccdl dataset type
        ##########
        # # remove first line which contains date
        # readme_file_contents_no_date = self.readme_file_contents.split("\n", 1)[1].strip()
        # readme_file_contents_no_date_bytes = readme_file_contents_no_date.encode("utf-8")
        # return hashlib.md5(readme_file_contents_no_date_bytes).hexdigest()
        return hashlib.md5(b"1").hexdigest()

    @staticmethod
    def get_combined_hash(data_hash: int, metadata_hash: int, readme_hash: int) -> int:
        concat_hash = str(data_hash) + str(metadata_hash) + str(readme_hash)
        return hash(concat_hash)


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
