from pathlib import Path
from typing import Dict
from zipfile import ZipFile

from django.conf import settings
from django.db import models

from typing_extensions import Self

from scpca_portal import common, metadata_file, readme_file, s3, utils
from scpca_portal.config.logging import get_and_configure_logger, log_func_run_time
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.library import Library

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
            logger.error("There are no libraries on the portal!")
            return

        libraries_metadata = utils.filter_dict_list_by_keys(
            [lib for library in libraries for lib in library.get_combined_library_metadata()],
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

    @log_func_run_time(logger)
    @classmethod
    def get_project_file(cls, project, download_config: Dict) -> Self | None:
        """
        Queries for a project's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = Library.get_project_libraries_from_download_config(project, download_config)
        # If the query returns empty, then an error occurred, and we should abort early
        if not libraries.exists():
            return

        libraries_metadata = [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]

        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        project_data_file_paths = project.get_download_config_file_paths(download_config)
        s3.download_input_files(
            library_data_file_paths + project_data_file_paths, project.s3_input_bucket
        )

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

            if not download_config.get("metadata_only", False):
                for file_path in library_data_file_paths:
                    zip_file.write(
                        Library.get_local_file_path(file_path),
                        Library.get_zip_file_path(file_path, download_config),
                    )
                for file_path in project_data_file_paths:
                    zip_file.write(
                        Library.get_local_file_path(file_path),
                        Library.get_zip_file_path(file_path, download_config),
                    )

        computed_file = cls(
            has_bulk_rna_seq=(
                download_config["modality"] == Library.Modalities.SINGLE_CELL
                and project.has_bulk_rna_seq
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

    @log_func_run_time(logger)
    @classmethod
    def get_sample_file(cls, sample, download_config: Dict) -> Self | None:
        """
        Queries for a sample's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = Library.get_sample_libraries_from_download_config(sample, download_config)
        # If the query returns empty, then an error occurred, and we should abort early
        if not libraries.exists():
            return

        libraries_metadata = [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]
        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        s3.download_input_files(library_data_file_paths, sample.project.s3_input_bucket)

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

            for file_path in library_data_file_paths:
                zip_file.write(
                    Library.get_local_file_path(file_path),
                    Library.get_zip_file_path(file_path, download_config),
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

    @property
    def download_url(self) -> str:
        """A temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            # Append the download date to the filename on download.
            date = utils.get_today_string()
            key_path = Path(self.s3_key)
            filename = f"{key_path.stem}_{date}{key_path.suffix}"

            return s3.generate_pre_signed_link(filename, self.s3_key, self.s3_bucket)

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
