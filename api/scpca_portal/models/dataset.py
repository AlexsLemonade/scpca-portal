import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import ccdl_datasets, common, metadata_file, readme_file
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import (
    CCDLDatasetNames,
    DatasetDataProjectConfig,
    DatasetFormats,
    JobStates,
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
    pending_at = models.DateTimeField(null=True)
    is_pending = models.BooleanField(default=False)
    processing_at = models.DateTimeField(null=True)
    is_processing = models.BooleanField(default=False)
    succeeded_at = models.DateTimeField(null=True)
    is_succeeded = models.BooleanField(default=False)
    failed_at = models.DateTimeField(null=True)
    is_failed = models.BooleanField(default=False)
    failed_reason = models.TextField(null=True)
    expires_at = models.DateTimeField(null=True)
    is_expired = models.BooleanField(default=False)  # Set by cronjob
    terminated_at = models.DateTimeField(null=True)
    is_terminated = models.BooleanField(default=False)
    terminated_reason = models.TextField(null=True)

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

    @classmethod
    def update_from_last_jobs(cls, datasets: List[Self]) -> None:
        """
        Updates datasets' state based on their latest jobs.
        """
        for dataset in datasets:
            dataset.update_from_last_job(save=False)

        updated_attrs = [
            "is_pending",
            "pending_at",
            "is_processing",
            "processing_at",
            "is_succeeded",
            "succeeded_at",
            "is_failed",
            "failed_at",
            "failed_reason",
            "is_terminated",
            "terminated_at",
            "terminated_reason",
        ]
        cls.objects.bulk_update(datasets, updated_attrs)

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

    def update_from_last_job(self, save: bool = True) -> None:
        """
        Updates the dataset's state based on the latest job.
        Make sure to set 'save' to False when calling this from bulk update methods
        or from instance methods that call save() within.
        """
        last_job = self.jobs.order_by("-pending_at").first()

        match last_job.state:
            case JobStates.PENDING:
                self.on_job_pending()
            case JobStates.PROCESSING:
                self.on_job_processing()
            case JobStates.SUCCEEDED:
                self.on_job_succeeded()
            case JobStates.FAILED:
                self.on_job_failed()
            case JobStates.TERMINATED:
                self.on_job_terminated()

        if save:
            self.save()

    def apply_job_state(self) -> None:
        """
        Sets the dataset state (flag, reason, timestamps) based on the last job state.
        Resets states before applying changes.
        """
        # TODO: Use common.FINAL_JOB_STATES
        FINAL_JOB_STATES = [
            JobStates.SUCCEEDED,
            JobStates.FAILED,
            JobStates.TERMINATED,
        ]

        # Resets all state flags and reasons
        for state in JobStates:
            state_str = state.lower()

            setattr(self, f"is_{state_str}", False)
            reason_attr = f"{state_str}_reason"

            if hasattr(self, reason_attr):
                setattr(self, reason_attr, None)

        # Resets timestamps (reset all for PENDING, otherwise FINAL_JOB_STATES)
        reset_states = JobStates if state == JobStates.PENDING else FINAL_JOB_STATES
        for state in reset_states:
            setattr(self, f"{state.lower()}_at", None)

        # Sets the current states
        last_job = self.jobs.order_by("-pending_at").first()
        state_str = last_job.state.lower()
        reason_attr = f"{state_str}_reason"

        setattr(self, f"is_{state_str}", True)
        setattr(self, f"{state_str}_at", make_aware(datetime.now()))
        if hasattr(self, f"{state_str}_reason"):
            setattr(self, f"{state_str}_reason", getattr(last_job, reason_attr))

    def on_job_pending(self) -> Self:
        """
        Marks the dataset as pending based on the last job.
        """
        self.apply_job_state()
        return self

    def on_job_processing(self) -> Self:
        """
        Marks the dataset as processing based on the last job.
        """
        self.apply_job_state()
        return self

    def on_job_succeeded(self) -> Self:
        """
        Marks the dataset as succeeded based on the last job.
        """
        self.apply_job_state()
        return self

    def on_job_failed(self) -> Self:
        """
        Marks the dataset as failed with the failure reason based on the last job.
        """
        self.apply_job_state()
        return self

    def on_job_terminated(self) -> Self:
        """
        Marks the dataset as terminated with the terminated reason based on the last job.
        """
        self.apply_job_state()
        return self

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
