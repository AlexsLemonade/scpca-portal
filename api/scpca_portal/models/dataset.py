import hashlib
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
from collections import Counter

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import ccdl_datasets, common, lockfile, metadata_file, readme_file
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

    @property
    def estimated_size_in_bytes(self) -> int:
        original_files_size = (
            self.original_files.aggregate(models.Sum("size_in_bytes")).get("size_in_bytes__sum")
            or 0
        )

        metadata_file_string = "".join(
            [file_content for _, _, file_content in self.get_metadata_file_contents()]
        )
        metadata_file_size = sys.getsizeof(metadata_file_string)

        readme_file_size = sys.getsizeof(self.readme_file_contents)

        return original_files_size + metadata_file_size + readme_file_size

    @property
    def diagnoses_summary(self) -> dict:
        """
        Counts present all diagnoses for samples in datasets.
        Returns dict where key is the diagnosis and value is a dict
        of project and sample counts.
        """
        # all diagnoses in the dataset
        if diagnoses := self.samples.values("diagnosis").annotate(
            samples=models.Count("scpca_id", distinct=True),
            projects=models.Count("project_id", distinct=True),
        ):
            return {d.pop("diagnosis"): d for d in diagnoses}

        return {}

    @property
    def files_summary(self) -> list[dict]:
        """
        Iterates over pre-defined file types that will be present in the dataset download.
        This break down looks at the type of information present in the individual files as well.
        Returns a list of dicts with name, samples_count, and format as keys.
        """

        # Name describes the type of files being summarized.
        # Filter describes how to match libraries in the dataset.
        # Format defaults to dataset format but can be overridden here.
        # Order is important, more specific should precede less specific.
        summary_queries = [
            {
                "name": "Single-nuclei multiplexed samples",
                "filter": {"is_multiplexed": True, "metadata__seq_unit": "nucleus"},
            },
            {
                "name": "Single-cell multiplexed samples",
                "filter": {"is_multiplexed": True},
            },
            {
                "name": "Single-nuclei samples",
                "filter": {"metadata__seq_unit": "nucleus"},
            },
            {
                "name": "Single-cell samples with CITE-seq",
                "filter": {"has_cite_seq_data": True},
            },
            {
                "name": "Single-cell samples",
                "filter": {"modality": Modalities.SINGLE_CELL},
            },
            {
                "name": "Spatial samples",
                "filter": {"modality": Modalities.SPATIAL},
                "format": "Spatial format",
            },
            {
                "name": "Bulk-RNA seq samples",
                "filter": {"modality": Modalities.BULK_RNA_SEQ},
                "format": ".tsv",
            },
        ]

        # cache
        dataset_samples = self.samples
        dataset_libraries = self.libraries

        seen_samples = set()
        summaries = []

        for file_summary_query in summary_queries:
            library_ids = (
                dataset_libraries.filter(**file_summary_query["filter"])
                .distinct()
                .values_list("scpca_id", flat=True)
            )

            if not library_ids:
                continue

            if samples_ids := (
                dataset_samples.filter(libraries__scpca_id__in=library_ids)
                .exclude(scpca_id__in=seen_samples)
                .values_list("scpca_id", flat=True)
            ):

                summaries.append(
                    {
                        "samples_count": len(samples_ids),
                        "name": file_summary_query["name"],
                        "format": file_summary_query.get(
                            "format", common.FORMAT_EXTENSIONS[self.format]
                        ),
                    }
                )

                seen_samples.update(samples_ids)

        return summaries

    @property
    def project_diagnoses(self) -> Dict:

        diagnoses_counts = {key: Counter() for key in self.data.keys()}

        for project_id, diagnosis in self.samples.values_list("project__scpca_id", "diagnosis"):
            diagnoses_counts[project_id].update({diagnosis: 1})

        return diagnoses_counts

    @property
    def stats(self) -> Dict:
        return {
            "current_data_hash": self.current_data_hash,
            "current_readme_hash": self.current_readme_hash,
            "current_metadata_hash": self.current_metadata_hash,
            "is_hash_changed": self.combined_hash != self.current_combined_hash,
            "uncompressed_size": self.estimated_size_in_bytes,
            "diagnoses_summary": self.diagnoses_summary,
            "files_summary": self.files_summary,
            "project_diagnoses": self.project_diagnoses,
        }

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
    def bulk_update_state(cls, datasets: List[Self]) -> None:
        """
        Updates state attributes of the given datasets in bulk.
        """
        STATE_UPDATE_ATTRS = [
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
        cls.objects.bulk_update(datasets, STATE_UPDATE_ATTRS)

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
                "includes_bulk": True,
                Modalities.SINGLE_CELL: (
                    list(single_cell_samples.values_list("scpca_id", flat=True))
                    if not self.ccdl_type.get("includes_merged")
                    else "MERGED"
                ),
                Modalities.SPATIAL: list(spatial_samples.values_list("scpca_id", flat=True)),
            }

        return data

    def contains_project_ids(self, project_ids: Set[str]) -> bool:
        """Returns whether or not the dataset contains samples in any of the passed projects."""
        return any(dataset_project_id in project_ids for dataset_project_id in self.data.keys())

    @property
    def has_lockfile_projects(self) -> bool:
        """Returns whether or not the dataset contains any project ids in the lockfile."""
        return self.contains_project_ids(set(lockfile.get_lockfile_project_ids()))

    @property
    def locked_projects(self) -> Iterable[Project]:
        """Returns a queryset of all of the dataset's locked project."""
        return self.projects.filter(is_locked=True)

    @property
    def has_locked_projects(self) -> bool:
        """Returns whether or not the dataset contains locked projects."""
        return self.locked_projects.exists()

    def apply_job_state(self, job) -> None:
        """
        Sets the dataset state (flag, reason, timestamps) based on the given job.
        Resets states before applying changes.
        """
        # Resets all state flags and reasons
        for state in JobStates:
            state_str = state.lower()

            setattr(self, f"is_{state_str}", False)
            reason_attr = f"{state_str}_reason"

            if hasattr(self, reason_attr):
                setattr(self, reason_attr, None)

        # Resets timestamps (reset all for PENDING, otherwise FINAL_JOB_STATES)
        reset_states = JobStates if state == JobStates.PENDING else common.FINAL_JOB_STATES
        for state in reset_states:
            setattr(self, f"{state.lower()}_at", None)

        # Sets new state based on the given job
        state_str = job.state.lower()
        reason_attr = f"{state_str}_reason"

        setattr(self, f"is_{state_str}", True)
        setattr(self, f"{state_str}_at", make_aware(datetime.now()))
        if hasattr(self, f"{state_str}_reason"):
            setattr(self, f"{state_str}_reason", getattr(job, reason_attr))

    @property
    def is_hash_changed(self) -> bool:
        """
        Determines whether or not a computed file should be generated for the instance dataset.
        Files should be processed for new datasets,
        or for datasets where at least one hash attribute has changed.
        """
        return self.combined_hash != self.current_combined_hash

    @property
    def is_hash_unchanged(self) -> bool:
        return not self.is_hash_changed

    @property
    def projects(self) -> Iterable[Project]:
        """Returns all Project instances associated with the Dataset."""
        if project_ids := self.data.keys():
            return Project.objects.filter(scpca_id__in=project_ids).order_by("scpca_id")
        return Project.objects.none()

    @property
    def samples(self) -> Iterable[Sample]:
        dataset_samples = Sample.objects.none()
        for project_id in self.data.keys():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL, Modalities.BULK_RNA_SEQ]:
                dataset_samples |= self.get_project_modality_samples(project_id, modality)

        return dataset_samples

    @property
    def libraries(self) -> Iterable[Library]:
        """Returns all of a Dataset's library, based on Data and Format attrs."""
        dataset_libraries = Library.objects.none()

        for project_id in self.data.keys():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL, Modalities.BULK_RNA_SEQ]:
                dataset_libraries |= self.get_project_modality_libraries(project_id, modality)

        return dataset_libraries

    @property
    def ccdl_type(self) -> Dict:
        return ccdl_datasets.TYPES.get(self.ccdl_name, {})

    @property
    def is_data_valid(self) -> bool:
        """Determines if the Dataset's Data attr is valid."""
        data_validator = DataValidator(self.data)
        return data_validator.is_valid

    def get_is_merged_project(self, project_id) -> bool:
        return self.data.get(project_id, {}).get(Modalities.SINGLE_CELL.value) == "MERGED"

    @property
    def original_files(self) -> Iterable[OriginalFile]:
        """Returns all of a Dataset's associated OriginalFiles."""
        files = OriginalFile.objects.none()

        if self.format == DatasetFormats.METADATA:
            return files

        for project_id, project_config in self.data.items():
            # add spatial files
            files |= OriginalFile.downloadable_objects.filter(
                project_id=project_id,
                is_spatial=True,
                sample_ids__overlap=project_config[DatasetDataProjectConfig.SPATIAL],
            )

            # add single-cell supplementary
            single_cell_sample_ids = [
                sample.scpca_id
                for sample in self.get_project_modality_samples(project_id, Modalities.SINGLE_CELL)
            ]
            files |= OriginalFile.downloadable_objects.filter(
                project_id=project_id,
                is_single_cell=True,
                is_supplementary=True,
                sample_ids__overlap=single_cell_sample_ids,
            )

            if self.get_is_merged_project(project_id):
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
                    sample_ids__overlap=single_cell_sample_ids,
                )
            if project_config[DatasetDataProjectConfig.INCLUDES_BULK]:
                files |= OriginalFile.downloadable_objects.filter(
                    project_id=project_id, is_bulk=True
                )

        return files

    @property
    def original_file_paths(self) -> Set[Path]:
        return {Path(of.s3_key) for of in self.original_files}

    def get_metadata_file_content(self, libraries: Iterable[Library]) -> str:
        """Return a string of the metadata file content of a collection of libraries."""
        libraries_metadata = Library.get_libraries_metadata(libraries)
        return metadata_file.get_file_contents(libraries_metadata)

    def get_project_modality_samples(
        self, project_id: str, modality: Modalities
    ) -> Iterable[Library]:
        """
        Takes project's scpca_id and a modality.
        Returns Sample instances defined in data attribute.
        """
        project_data = self.data.get(project_id, {})

        project_samples = Sample.objects.filter(project__scpca_id=project_id)

        if modality is Modalities.SINGLE_CELL and self.get_is_merged_project(project_id):
            return project_samples.filter(has_single_cell_data=True)

        if modality is Modalities.BULK_RNA_SEQ and project_data.get(
            DatasetDataProjectConfig.INCLUDES_BULK
        ):
            return project_samples.filter(has_bulk_rna_seq=True)

        return project_samples.filter(scpca_id__in=project_data.get(modality, []))

    def get_project_modality_libraries(
        self, project_id: str, modality: Modalities
    ) -> Iterable[Library]:
        """
        Takes project's scpca_id and a modality.
        Returns Library instances associated with Samples defined in data attribute.
        """
        libraries = Library.objects.none()

        if samples := self.get_project_modality_samples(project_id, modality):
            libraries = Library.objects.filter(samples__in=samples, modality=modality).distinct()

        if self.format != DatasetFormats.METADATA and modality != Modalities.BULK_RNA_SEQ:
            libraries = libraries.filter(formats__contains=[self.format])

        return libraries

    def get_project_modality_metadata_file_content(
        self, project_id: str, modality: Modalities
    ) -> str:
        """Return a string of the metadata file for a project and modality combination."""
        libraries = self.get_project_modality_libraries(project_id, modality)
        return self.get_metadata_file_content(libraries)

    def get_metadata_file_contents(self) -> List[tuple[str | None, Modalities | None, str]]:
        """
        Return a list of three element tuples which includes the project_id, modality,
        and their associatied metadata file contents as a string.
        """
        metadata_file_contents = []
        for project_id, project_config in self.data.items():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]:
                if not project_config.get(modality.value, []):
                    continue

                metadata_file_content = self.get_project_modality_metadata_file_content(
                    project_id, modality
                )
                metadata_file_contents.append((project_id, modality, metadata_file_content))
        return metadata_file_contents

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
        all_metadata_file_contents = [
            file_content for _, _, file_content in self.get_metadata_file_contents()
        ]
        concat_all_metadata_file_contents = "".join(sorted(all_metadata_file_contents))
        metadata_file_contents_bytes = concat_all_metadata_file_contents.encode("utf-8")
        return hashlib.md5(metadata_file_contents_bytes).hexdigest()

    @property
    def current_readme_hash(self) -> str:
        """Computes and returns the current readme hash."""
        # the first line in the readme file contains the current date
        # we must remove this before hashing
        readme_file_contents = self.readme_file_contents.split("\n", 1)[1].strip()
        readme_file_contents_bytes = readme_file_contents.encode("utf-8")
        return hashlib.md5(readme_file_contents_bytes).hexdigest()

    @property
    def combined_hash(self) -> str | None:
        """
        Combines, computes and returns the combined cached data, metadata and readme hashes.
        """
        # Return None if hashes have not been calculated yet
        if not (self.data_hash and self.metadata_hash and self.readme_hash):
            return None
        concat_hash = self.data_hash + self.metadata_hash + self.readme_hash
        return hashlib.md5(concat_hash.encode("utf-8")).hexdigest()

    @property
    def current_combined_hash(self) -> str | None:
        """
        Combines, computes and returns the combined current data, metadata and readme hashes.
        """
        concat_hash = self.current_data_hash + self.current_metadata_hash + self.current_readme_hash
        return hashlib.md5(concat_hash.encode("utf-8")).hexdigest()

    @property
    def valid_ccdl_dataset(self) -> bool:
        if not self.libraries.exists():
            return False

        return self.projects.filter(**self.ccdl_type.get("constraints", {})).exists()

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

    def _validate_includes_bulk(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.INCLUDES_BULK):
            return isinstance(value, bool)

        return True

    def _validate_single_cell(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.SINGLE_CELL):
            if value == "MERGED":
                return True
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
