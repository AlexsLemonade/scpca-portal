import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Set

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import common, lockfile, metadata_file, readme_file, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetDataProjectConfig, DatasetFormats, JobStates, Modalities
from scpca_portal.models.api_token import APIToken
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.library import Library
from scpca_portal.models.original_file import OriginalFile
from scpca_portal.models.project import Project
from scpca_portal.models.sample import Sample

logger = get_and_configure_logger(__name__)


class DatasetABC(TimestampedModel, models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-editable
    format = models.TextField(choices=DatasetFormats.choices)  # Required upon creation
    data = models.JSONField(default=dict)
    email = models.EmailField(null=True)
    start = models.BooleanField(default=False)

    # Hashes
    data_hash = models.CharField(max_length=32, null=True)
    metadata_hash = models.CharField(max_length=32, null=True)
    readme_hash = models.CharField(max_length=32, null=True)
    combined_hash = models.CharField(max_length=32, null=True)

    # Cached File Attrs
    includes_files_bulk = models.BooleanField(default=False)
    includes_files_cite_seq = models.BooleanField(default=False)
    includes_files_merged = models.BooleanField(default=False)
    includes_files_multiplexed = models.BooleanField(default=False)
    estimated_size_in_bytes = models.BigIntegerField(default=0)

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
        related_name="%(class)s",
    )
    token = models.ForeignKey(
        APIToken,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_set",
    )
    download_tokens = models.ManyToManyField(
        APIToken,
        related_name="downloaded_%(class)s_set",
    )
    jobs = GenericRelation(
        "scpca_portal.Job",
        content_type_field="dataset_content_type",
        object_id_field="dataset_object_id",
    )

    def __str__(self):
        return f"Dataset {self.id}"

    def save(self, *args, **kwargs):
        """
        In addition to the built-in object saving functionality,
        cached attributes should be re-computed and re-assigned on each save.
        """

        # file hashes
        self.data_hash, self.metadata_hash, self.readme_hash, self.combined_hash = self.get_hashes()

        # file items
        self.includes_files_bulk = self.get_includes_files_bulk()
        self.includes_files_cite_seq = self.get_includes_files_cite_seq()
        self.includes_files_merged = self.get_includes_files_merged()
        self.includes_files_multiplexed = self.get_includes_files_multiplexed()

        # stats property attributes
        self.estimated_size_in_bytes = self.get_estimated_size_in_bytes()

        super().save(*args, **kwargs)

    def get_class(self) -> models.Model:
        return self._meta.model

    # HASHING AND CACHED ATTR LOGIC
    def get_hashes(self) -> tuple[str, str, str, str]:
        """Computes and returns data, metadata, readme, and combined hashes."""
        data_hash = self.current_data_hash
        metadata_hash = self.current_metadata_hash
        readme_hash = self.current_readme_hash
        combined_hash = self.get_current_combined_hash(data_hash, metadata_hash, readme_hash)

        return (data_hash, metadata_hash, readme_hash, combined_hash)

    @property
    def current_data_hash(self) -> str:
        """Computes and returns the current data hash."""
        original_file_hashes = self.original_files.values_list("hash", flat=True)
        return utils.hash_values(original_file_hashes)

    @property
    def current_metadata_hash(self) -> str:
        """Computes and returns the current metadata hash."""
        all_metadata_file_contents = [
            file_content for _, _, file_content in self.get_metadata_file_contents()
        ]
        return utils.hash_values(all_metadata_file_contents)

    @property
    def current_readme_hash(self) -> str:
        """Computes and returns the current readme hash."""
        # the first line in the readme file contains the current date
        # we must remove this before hashing
        readme_file_contents = self.readme_file_contents.split("\n", 1)[1].strip()
        return utils.hash_values([readme_file_contents])

    @staticmethod
    def get_current_combined_hash(data_hash: str, metadata_hash: str, readme_hash: str) -> str:
        """
        Combines, computes and returns the combined current data, metadata and readme hashes.
        """
        return utils.hash_values([data_hash, metadata_hash, readme_hash])

    @property
    def is_hash_changed(self) -> bool:
        """
        Determines whether or not a computed file should be generated for the instance dataset.
        Files should be processed for new datasets,
        or for datasets where at least one hash attribute has changed.
        """
        current_combined_hash = self.get_current_combined_hash(
            self.current_data_hash, self.current_metadata_hash, self.current_readme_hash
        )
        return current_combined_hash != self.combined_hash

    @property
    def is_hash_unchanged(self) -> bool:
        return not self.is_hash_changed

    def get_metadata_file_content(self, libraries: Iterable[Library]) -> str:
        """Return a string of the metadata file content of a collection of libraries."""
        libraries_metadata = Library.get_libraries_metadata(libraries)
        return metadata_file.get_file_contents(libraries_metadata)

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
        # We only return one metadata file for all metadata datasets
        # TODO: if we need to put project metadata files in a project folder,
        # add a condition "not ccdl_project_id" to this line
        if self.format == DatasetFormats.METADATA:
            return [(None, None, self.get_metadata_file_content(self.libraries))]

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
        return readme_file.get_file_contents_dataset_new(self)

    def get_includes_files_bulk(self) -> bool:
        return self.bulk_single_cell_projects.exists()

    def get_includes_files_cite_seq(self) -> bool:
        return self.cite_seq_projects.exists()

    def get_includes_files_merged(self) -> bool:
        return self.merged_projects.exists()

    def get_includes_files_multiplexed(self) -> bool:
        return self.multiplexed_projects.exists()

    @property
    def pretty_estimated_size_in_bytes(self):
        return utils.format_bytes(self.estimated_size_in_bytes)

    def get_estimated_size_in_bytes(self) -> int:
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

    # ASSOCIATIONS WITH OTHER MODELS
    @property
    def projects(self) -> Iterable[Project]:
        """Returns all project instances associated with the dataset."""
        if project_ids := self.data.keys():
            return Project.objects.filter(scpca_id__in=project_ids).order_by("scpca_id")
        return Project.objects.none()

    @property
    def spatial_projects(self) -> Iterable[Project]:
        """
        Returns all project instances which have spatial data
        with spatial samples requested in the data attribute.
        """
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(Modalities.SPATIAL, [])
        ]:
            return self.projects.filter(has_spatial_data=True, scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def single_cell_projects(self) -> Iterable[Project]:
        """
        Returns all project instances which have single cell data
        with single cell samples requested in the data attribute.
        """
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(Modalities.SINGLE_CELL)
        ]:
            return self.projects.filter(has_single_cell_data=True, scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def bulk_single_cell_projects(self) -> Iterable[Project]:
        """
        Returns all project instances which have bulk data
        where bulk was requested in the data attribute.
        """
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(DatasetDataProjectConfig.INCLUDES_BULK)
        ]:
            return self.projects.filter(has_bulk_rna_seq=True, scpca_id__in=project_ids)

        return Project.objects.none()

    @property
    def cite_seq_projects(self) -> Iterable[Project]:
        """
        Returns all project instances associated with the dataset
        which have cite seq data.
        """
        return self.projects.filter(has_cite_seq_data=True)

    @property
    def merged_projects(self) -> Iterable[Project]:
        """
        Returns all project instances which have merged data
        where merged was requested in the data attribute single cell field.
        """
        if project_ids := [
            project_id
            for project_id, project_options in self.data.items()
            if project_options.get(Modalities.SINGLE_CELL) == "MERGED"
        ]:
            requested_merged_projects = self.projects.filter(scpca_id__in=project_ids)

            if self.format == DatasetFormats.SINGLE_CELL_EXPERIMENT:
                return requested_merged_projects.filter(includes_merged_sce=True)

            if self.format == DatasetFormats.ANN_DATA:
                return requested_merged_projects.filter(includes_merged_anndata=True)

        return Project.objects.none()

    @property
    def multiplexed_projects(self) -> Iterable[Project]:
        """
        Returns all project instances which have multiplexed data.
        """
        # Multiplexed samples are not available with anndata
        if self.format == DatasetFormats.ANN_DATA:
            return Project.objects.none()

        multiplexed_samples = self.get_selected_samples([Modalities.SINGLE_CELL]).filter(
            has_multiplexed_data=True
        )
        return Project.objects.filter(samples__in=multiplexed_samples).distinct()

    def contains_project_ids(self, project_ids: Set[str]) -> bool:
        """Returns whether or not the dataset contains samples in any of the passed projects."""
        return any(dataset_project_id in project_ids for dataset_project_id in self.data.keys())

    @property
    def has_lockfile_projects(self) -> bool:
        """Returns whether or not the dataset contains any project ids in the lockfile."""
        return self.contains_project_ids(set(lockfile.get_locked_project_ids()))

    @property
    def locked_projects(self) -> Iterable[Project]:
        """Returns a queryset of all of the dataset's locked project."""
        return self.projects.filter(is_locked=True)

    @property
    def has_locked_projects(self) -> bool:
        """Returns whether or not the dataset contains locked projects."""
        return self.locked_projects.exists()

    @property
    def is_locked(self) -> bool:
        """
        Returns whether a dataset contains projects which are locked
        or which have project ids in the lockfile.
        """
        return self.has_locked_projects or self.has_lockfile_projects

    @property
    def samples(self) -> Iterable[Sample]:
        """
        Returns a queryset of all samples contained in data attribute.
        If a sample is present in more than one modality, it will be
        duplicated in the resulting queryset.
        """
        return self.get_selected_samples(
            [Modalities.SINGLE_CELL, Modalities.SPATIAL, Modalities.BULK_RNA_SEQ]
        )

    def get_selected_samples(self, modalities: Iterable[Modalities] = []) -> Iterable[Sample]:
        """
        Returns a queryset of samples for the specified modalities
        contained in data attribute.
        """
        dataset_samples = Sample.objects.none()
        for project_id in self.data.keys():
            for modality in modalities:
                dataset_samples |= self.get_project_modality_samples(project_id, modality)

        return dataset_samples

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

    @property
    def libraries(self) -> Iterable[Library]:
        """Returns all of a Dataset's library, based on Data and Format attrs."""
        dataset_libraries = Library.objects.none()

        for project_id in self.data.keys():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL, Modalities.BULK_RNA_SEQ]:
                dataset_libraries |= self.get_project_modality_libraries(project_id, modality)

        return dataset_libraries

    def get_project_modality_libraries(
        self, project_id: str, modality: Modalities
    ) -> Iterable[Library]:
        """
        Takes project's scpca_id and a modality.
        Returns Library instances associated with Samples defined in data attribute.
        """
        libraries = Library.objects.filter(
            samples__in=self.get_project_modality_samples(project_id, modality), modality=modality
        ).distinct()

        # Both spatial and bulk modalities, as well as metadata dataset format,
        # don't need to be queried on format
        if modality == Modalities.SINGLE_CELL and self.format != DatasetFormats.METADATA:
            libraries = libraries.filter(formats__contains=[self.format])

        return libraries

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

    @property
    def computed_file_local_path(self) -> Path:
        return settings.OUTPUT_DATA_PATH / ComputedFile.get_dataset_file_s3_key(self)

    @property
    def download_filename(self) -> str:
        output_format = "-".join(self.format.split("_")).lower()
        date = utils.get_today_string()

        return f"{self.id}_{output_format}_{date}.zip"

    @property
    def download_url(self) -> str | None:
        """A temporary URL from which the file can be downloaded."""
        if not self.computed_file:
            return None

        return self.computed_file.get_dataset_download_url(self.download_filename)

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
