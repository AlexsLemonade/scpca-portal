import subprocess
from pathlib import Path
from threading import Lock
from typing import Dict
from zipfile import ZipFile

from django.conf import settings
from django.db import models

import boto3
from botocore.client import Config
from typing_extensions import Self

from scpca_portal import common, metadata_file, readme_file, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.library import Library

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


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

        return common.OUTPUT_DATA_PATH / "_".join(file_name_parts)

    @staticmethod
    def get_local_sample_metadata_path(sample, download_config: Dict) -> Path:
        file_name_parts = sample.multiplexed_ids
        file_name_parts.extend(
            [download_config["modality"], download_config["format"], "METADATA.tsv"]
        )
        return common.OUTPUT_DATA_PATH / "_".join(file_name_parts)

    @classmethod
    def get_project_file(cls, project, download_config: Dict, computed_file_name: str) -> Self:
        """
        Queries for a project's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = Library.get_project_libraries_from_download_config(project, download_config)
        # If the query return empty, then an error occurred, and we should abort early
        if not libraries.exists():
            return

        libraries_metadata = [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]
        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        project_data_file_paths = project.get_download_config_file_paths(download_config)

        zip_file_path = common.OUTPUT_DATA_PATH / computed_file_name
        with ZipFile(zip_file_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(
                readme_file.OUTPUT_NAME,
                readme_file.get_file_contents(download_config, project),
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
                if download_config["modality"] == "SPATIAL":
                    for library in libraries:
                        file_path = Path(
                            "/".join(
                                [
                                    project.scpca_id,
                                    library.samples.first().scpca_id,
                                    f"{library.scpca_id}_spatial",
                                    f"{library.scpca_id}_metadata.json",
                                ]
                            )
                        )
                        zip_file.write(
                            Library.get_local_file_path(file_path),
                            file_path.relative_to(f"{project.scpca_id}/"),
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
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=computed_file_name,
            size_in_bytes=zip_file_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in libraries
            ),
        )

        return computed_file

    @classmethod
    def get_sample_file(
        cls, sample, download_config: Dict, computed_file_name: str, lock: Lock
    ) -> Self:
        """
        Queries for a sample's libraries according to the given download options configuration,
        writes the queried libraries to a libraries metadata file,
        computes a zip archive with library data, metadata and readme files, and
        creates a ComputedFile object which it then saves to the db.
        """
        libraries = Library.get_sample_libraries_from_download_config(sample, download_config)
        # If the query return empty, then an error occurred, and we should abort early
        if not libraries.exists():
            return

        libraries_metadata = [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]
        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]

        zip_file_path = common.OUTPUT_DATA_PATH / computed_file_name
        # This lock is primarily for multiplex. We added it here as a patch to keep things generic.
        with lock:  # It should be removed later for a cleaner solution.
            if not zip_file_path.exists():
                with ZipFile(zip_file_path, "w") as zip_file:
                    # Readme file
                    zip_file.writestr(
                        readme_file.OUTPUT_NAME,
                        readme_file.get_file_contents(download_config, sample.project),
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

                    if download_config["modality"] == "SPATIAL":
                        for library in libraries:
                            file_path = Path(
                                "/".join(
                                    [
                                        sample.project.scpca_id,
                                        sample.scpca_id,
                                        f"{library.scpca_id}_spatial",
                                        f"{library.scpca_id}_metadata.json",
                                    ]
                                )
                            )
                            zip_file.write(
                                Library.get_local_file_path(file_path),
                                file_path.relative_to(
                                    f"{sample.project.scpca_id}/{sample.scpca_id}/"
                                ),
                            )

        computed_file = cls(
            has_cite_seq_data=sample.has_cite_seq_data,
            has_multiplexed_data=libraries.filter(is_multiplexed=True).exists(),
            format=download_config.get("format"),
            includes_celltype_report=(not sample.is_cell_line),
            modality=download_config.get("modality"),
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=computed_file_name,
            sample=sample,
            size_in_bytes=zip_file_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in libraries
            ),
        )

        return computed_file

    @property
    def download_url(self):
        """A temporary URL from which the file can be downloaded."""
        return self.create_download_url()

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
        return common.OUTPUT_DATA_PATH / self.s3_key

    def create_download_url(self):
        """Creates a temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            # Append the download date to the filename on download.
            date = utils.get_today_string()
            s3_key = Path(self.s3_key)

            return s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.s3_bucket,
                    "Key": self.s3_key,
                    "ResponseContentDisposition": (
                        f"attachment; filename = {s3_key.stem}_{date}{s3_key.suffix}"
                    ),
                },
                ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
            )

    def upload_s3_file(self):
        """Upload a computed file to S3 using the AWS CLI tool."""

        aws_path = f"s3://{settings.AWS_S3_BUCKET_NAME}/{self.s3_key}"
        command_parts = ["aws", "s3", "cp", str(self.zip_file_path), aws_path]

        logger.info(f"Uploading {self}")
        subprocess.check_call(command_parts)

    def delete_s3_file(self, force=False):
        # If we're not running in the cloud then we shouldn't try to
        # delete something from S3 unless force is set.
        if not settings.UPDATE_S3_DATA and not force:
            return False

        try:
            s3.delete_object(Bucket=self.s3_bucket, Key=self.s3_key)
        except Exception:
            logger.exception(
                "Failed to delete S3 object for Computed File.",
                computed_file=self.id,
                s3_object=self.s3_key,
            )
            return False

        return True

    def clean_up_local_computed_file(self):
        """Delete local computed file."""
        self.zip_file_path.unlink(missing_ok=True)
