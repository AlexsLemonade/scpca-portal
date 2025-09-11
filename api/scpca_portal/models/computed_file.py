from pathlib import Path
from typing import Dict
from zipfile import ZipFile

from django.conf import settings
from django.db import models

from typing_extensions import Self

from scpca_portal import common, metadata_file, readme_file, s3, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.exceptions import DatasetLockedProjectError, DatasetMissingLibrariesError
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.library import Library
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)


class ComputedFile(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    class OutputFileModalities:
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    class OutputFileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        )

    format = models.TextField(choices=OutputFileFormats.CHOICES, null=True)
    includes_merged = models.BooleanField(default=False)
    modality = models.TextField(choices=OutputFileModalities.CHOICES, null=True)
    metadata_only = models.BooleanField(default=False)
    portal_metadata_only = models.BooleanField(default=False)
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    workflow_version = models.TextField()
    includes_celltype_report = models.BooleanField(default=False)

    project = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, related_name="project_computed_files"
    )
    sample = models.ForeignKey(
        "Sample", null=True, on_delete=models.CASCADE, related_name="sample_computed_files"
    )

    def __str__(self):
        return (
            f"'{self.project or self.sample}' "
            f"{dict(self.OutputFileModalities.CHOICES).get(self.modality, 'No Modality')} "
            f"{dict(self.OutputFileFormats.CHOICES).get(self.format, 'No Format')} "
            f"computed file ({self.size_in_bytes}B)"
        )

    @staticmethod
    def get_local_project_metadata_path(project, download_config: Dict) -> Path:
        file_name_parts = [project.scpca_id]
        if not download_config["metadata_only"]:
            file_name_parts.extend([download_config["modality"], download_config["format"]])
            if project.has_multiplexed_data and not download_config["excludes_multiplexed"]:
                file_name_parts.append("MULTIPLEXED")
        file_name_parts.append("METADATA.tsv")

        return settings.OUTPUT_DATA_PATH / "_".join(file_name_parts)

    @staticmethod
    def get_local_sample_metadata_path(sample, download_config: Dict) -> Path:
        file_name_parts = sample.multiplexed_ids
        file_name_parts.extend(
            [download_config["modality"], download_config["format"], "METADATA.tsv"]
        )
        return settings.OUTPUT_DATA_PATH / "_".join(file_name_parts)

    @staticmethod
    def get_local_portal_metadata_path() -> Path:
        return settings.OUTPUT_DATA_PATH / common.PORTAL_METADATA_COMPUTED_FILE_NAME

    @staticmethod
    def get_local_file_path(download_config: Dict) -> Path:
        """Takes a download_config dictionary and returns the filepath
        where the zipfile will be saved locally before upload."""
        if download_config is common.PORTAL_METADATA_DOWNLOAD_CONFIG:
            return settings.OUTPUT_DATA_PATH / common.PORTAL_METADATA_COMPUTED_FILE_NAME

    @staticmethod
    def get_output_file_parent_dir(
        original_file,
        dataset,
    ) -> Path:
        """Return the correct output file parent directory of the passed original_file."""
        if original_file.is_bulk:
            return Path(f"{original_file.project_id}_bulk_rna")

        # spatial / unmerged single cell
        modality = Modalities.SINGLE_CELL if original_file.is_single_cell else Modalities.SPATIAL
        modality_formatted = modality.value.lower().replace("_", "-")
        parent_dir = Path(f"{original_file.project_id}_{modality_formatted}")

        # merged single cell
        # only single cell supplementary and merged files should be nested in a merge directory
        if dataset.get_is_merged_project(original_file.project_id) and not original_file.is_spatial:
            parent_dir = Path(f"{original_file.project_id}_single-cell_merged")

            # only library supplementary files should be in an individual_reports dir,
            # not the merged supplementary file
            if original_file.is_supplementary and not original_file.is_merged:
                return parent_dir / Path(common.MERGED_REPORTS_PREFEX_DIR)

        return parent_dir

    @staticmethod
    def get_original_file_zip_path(original_file: OriginalFile, dataset) -> Path:
        """Return an original file's path for the zip file being computed."""
        # always remove project directory
        zip_file_path = original_file.s3_key_path.relative_to(
            Path(original_file.s3_key_info.project_id_part)
        )
        if original_file.is_bulk or original_file.is_merged:
            # bulk and merged files come in nested directories, which should be popped off
            zip_file_path = Path(*zip_file_path.parts[1:])

        parent_dir = ComputedFile.get_output_file_parent_dir(original_file, dataset)
        zip_file_path = parent_dir / zip_file_path

        # Make sure that multiplexed sample files are adequately transformed by default
        return utils.path_replace(
            zip_file_path,
            common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER,
            common.MULTIPLEXED_SAMPLES_OUTPUT_DELIMETER,
        )

    @staticmethod
    def get_metadata_file_zip_path(project_id: str, modality: Modalities, dataset) -> Path:
        """Return metadata file path, modality name inside of project_modality directory."""
        # Metadata only downloads are not associated with a specific project_id or modality
        if dataset.format == DatasetFormats.METADATA:
            return Path("metadata.tsv")

        modality_formatted = modality.value.lower().replace("_", "-")
        metadata_file_name_path = Path(f"{modality_formatted}_metadata.tsv")

        metadata_dir = f"{project_id}_{modality_formatted}"
        if dataset.get_is_merged_project(project_id):
            metadata_dir += "_merged"

        return Path(metadata_dir) / Path(metadata_file_name_path)

    @classmethod
    def get_dataset_file_s3_key(cls, dataset) -> str:
        return f"{dataset.id}.zip"

    @classmethod
    def get_dataset_file(cls, dataset) -> Self:
        """
        Computes a given dataset's zip archive and returns a corresponding ComputedFile object.
        """
        if dataset.has_lockfile_projects or dataset.has_locked_projects:
            raise DatasetLockedProjectError(dataset)

        # If the query returns empty, then throw an error occurred.
        if not dataset.libraries.exists():
            raise DatasetMissingLibrariesError(dataset)

        dataset_original_files = dataset.original_files
        for project in dataset.projects:
            s3.download_files(dataset_original_files.filter(project_id=project.scpca_id))
            if dataset.has_lockfile_projects or dataset.has_locked_projects:
                raise DatasetLockedProjectError(dataset)

        with ZipFile(dataset.computed_file_local_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(readme_file.OUTPUT_NAME, dataset.readme_file_contents)

            # Metadata files
            for project_id, modality, metadata_file_content in dataset.get_metadata_file_contents():
                zip_file.writestr(
                    str(ComputedFile.get_metadata_file_zip_path(project_id, modality, dataset)),
                    metadata_file_content,
                )

            # Original files
            for original_file in dataset.original_files:
                zip_file.write(
                    original_file.local_file_path,
                    ComputedFile.get_original_file_zip_path(original_file, dataset),
                )

        computed_file = cls(
            dataset=dataset,
            has_bulk_rna_seq=(
                any(
                    True
                    for project_id, project_config in dataset.data.items()
                    if project_config.get("includes_bulk")
                    and dataset.projects.filter(scpca_id=project_id, has_bulk_rna_seq=True).exists()
                )
            ),
            has_cite_seq_data=dataset.libraries.filter(has_cite_seq_data=True).exists(),
            has_multiplexed_data=dataset.libraries.filter(is_multiplexed=True).exists(),
            format=dataset.ccdl_type.get("format"),
            includes_celltype_report=dataset.projects.filter(samples__is_cell_line=False).exists(),
            includes_merged=dataset.ccdl_type.get("includes_merged"),
            modality=dataset.ccdl_type.get("modality"),
            metadata_only=dataset.ccdl_name == DatasetFormats.METADATA,
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key=cls.get_dataset_file_s3_key(dataset),
            size_in_bytes=dataset.computed_file_local_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in dataset.libraries
            ),
        )

        return computed_file

    @classmethod
    def get_portal_metadata_file(cls, projects, download_config: Dict) -> Self:
        """
        Queries all libraries to aggregate the combined metadata,
        writes the aggregated combined metadata to a portal metadata file,
        computes a zip archive with metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = Library.objects.all()
        # If the query returns empty, then an error occurred, and we should abort early
        if not libraries.exists():
            raise ValueError("There are no libraries on the portal!")

        libraries_metadata = utils.filter_dict_list_by_keys(
            Library.get_libraries_metadata(libraries),
            common.METADATA_COLUMN_SORT_ORDER,
        )

        zip_file_path = cls.get_local_file_path(download_config)
        with ZipFile(zip_file_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(
                readme_file.OUTPUT_NAME,
                readme_file.get_file_contents(
                    download_config,
                    projects,
                ),
            )
            # Metadata file
            zip_file.writestr(
                metadata_file.get_file_name(download_config),
                metadata_file.get_file_contents(libraries_metadata),
            )

        computed_file = cls(
            format=download_config.get("format"),
            modality=download_config.get("modality"),
            includes_merged=download_config.get("includes_merged"),
            metadata_only=download_config.get("metadata_only"),
            portal_metadata_only=download_config.get("portal_metadata_only"),
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key=common.PORTAL_METADATA_COMPUTED_FILE_NAME,
            size_in_bytes=zip_file_path.stat().st_size,
        )

        return computed_file

    @classmethod
    def get_project_file(cls, project, download_config: Dict) -> Self:
        """
        Queries for a project's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = project.get_libraries(download_config)
        # If the query returns empty, then throw an error occurred.
        if not libraries.exists():
            raise ValueError("Unable to find libraries for download_config.")

        libraries_metadata = Library.get_libraries_metadata(libraries)
        original_files = Library.get_libraries_original_files(libraries, download_config)
        s3.download_files(original_files)

        zip_file_path = settings.OUTPUT_DATA_PATH / project.get_output_file_name(download_config)
        with ZipFile(zip_file_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(
                readme_file.OUTPUT_NAME,
                readme_file.get_file_contents(download_config, [project]),
            )

            # Metadata file
            zip_file.writestr(
                metadata_file.get_file_name(download_config),
                metadata_file.get_file_contents(libraries_metadata),
            )

            # Original files
            if not download_config.get("metadata_only", False):
                for original_file in original_files:
                    zip_file.write(
                        original_file.local_file_path,
                        original_file.get_zip_file_path(download_config),
                    )

        computed_file = cls(
            has_bulk_rna_seq=(
                download_config["modality"] == Modalities.SINGLE_CELL and project.has_bulk_rna_seq
            ),
            has_cite_seq_data=project.has_cite_seq_data,
            has_multiplexed_data=libraries.filter(is_multiplexed=True).exists(),
            format=download_config.get("format"),
            includes_celltype_report=project.samples.filter(is_cell_line=False).exists(),
            includes_merged=download_config.get("includes_merged"),
            modality=download_config.get("modality"),
            metadata_only=download_config.get("metadata_only"),
            project=project,
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key=project.get_output_file_name(download_config),
            size_in_bytes=zip_file_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in libraries
            ),
        )

        return computed_file

    @classmethod
    def get_sample_file(cls, sample, download_config: Dict) -> Self:
        """
        Queries for a sample's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = sample.get_libraries(download_config)
        # If the query returns empty, then throw an error occurred.
        if not libraries.exists():
            raise ValueError("Unable to find libraries for download_config.")

        libraries_metadata = Library.get_libraries_metadata(libraries)
        original_files = Library.get_libraries_original_files(libraries, download_config)
        s3.download_files(original_files)

        zip_file_path = settings.OUTPUT_DATA_PATH / sample.get_output_file_name(download_config)
        with ZipFile(zip_file_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(
                readme_file.OUTPUT_NAME,
                readme_file.get_file_contents(download_config, [sample.project]),
            )
            # Metadata file
            zip_file.writestr(
                metadata_file.get_file_name(download_config),
                metadata_file.get_file_contents(libraries_metadata),
            )

            # Original files
            for original_file in original_files:
                zip_file.write(
                    original_file.local_file_path,
                    original_file.get_zip_file_path(download_config),
                )

        computed_file = cls(
            has_cite_seq_data=sample.has_cite_seq_data,
            has_multiplexed_data=libraries.filter(is_multiplexed=True).exists(),
            format=download_config.get("format"),
            includes_celltype_report=(not sample.is_cell_line),
            modality=download_config.get("modality"),
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key=sample.get_output_file_name(download_config),
            sample=sample,
            size_in_bytes=zip_file_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in libraries
            ),
        )

        return computed_file

    def get_dataset_download_url(self, download_filename: str) -> str | None:
        """Return the presigned url on the associated dataset according to the passed filename."""
        if not (self.s3_bucket and self.s3_key):
            return None

        return s3.generate_pre_signed_link(download_filename, self.s3_key, self.s3_bucket)

    @property
    def download_filename(self) -> str:
        # Append the download date to the filename on download.
        date = utils.get_today_string()
        key_path = Path(self.s3_key)
        return f"{key_path.stem}_{date}{key_path.suffix}"

    @property
    def download_url(self) -> str:
        """A temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            return s3.generate_pre_signed_link(self.download_filename, self.s3_key, self.s3_bucket)

    @property
    def is_project_multiplexed_zip(self):
        return (
            self.modality == ComputedFile.OutputFileModalities.SINGLE_CELL
            and self.has_multiplexed_data
        )

    @property
    def is_project_single_cell_zip(self):
        return (
            self.modality == ComputedFile.OutputFileModalities.SINGLE_CELL
            and not self.has_multiplexed_data
        )

    @property
    def is_project_spatial_zip(self):
        return self.modality == ComputedFile.OutputFileModalities.SPATIAL

    @property
    def metadata_file_name(self):
        if self.is_project_multiplexed_zip or self.is_project_single_cell_zip:
            return ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
        if self.is_project_spatial_zip:
            return ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME
        return ComputedFile.MetadataFilenames.METADATA_ONLY_FILE_NAME

    @property
    def zip_file_path(self):
        return settings.OUTPUT_DATA_PATH / self.s3_key

    def get_multiplexed_computed_files(self):
        """
        Return computed file objects for all associated multiplexed samples.
        """
        computed_files = [self]
        for sample in self.sample.multiplexed_with_samples:
            sample_computed_file = ComputedFile(
                format=self.format,
                includes_merged=self.includes_merged,
                modality=self.modality,
                metadata_only=self.metadata_only,
                portal_metadata_only=self.portal_metadata_only,
                s3_bucket=self.s3_bucket,
                s3_key=self.s3_key,
                size_in_bytes=self.size_in_bytes,
                workflow_version=self.workflow_version,
                includes_celltype_report=self.includes_celltype_report,
                has_bulk_rna_seq=self.has_bulk_rna_seq,
                has_cite_seq_data=self.has_cite_seq_data,
                has_multiplexed_data=self.has_multiplexed_data,
                sample=sample,
            )

            computed_files.append(sample_computed_file)

        return computed_files

    def clean_up_local_computed_file(self):
        """Delete local computed file."""
        self.zip_file_path.unlink(missing_ok=True)

    def purge(self, delete_from_s3: bool = False) -> None:
        """Purges a computed file, optionally deleting it from S3."""
        if delete_from_s3:
            s3.delete_output_file(self.s3_key, self.s3_bucket)
        self.delete()
