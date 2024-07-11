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

from scpca_portal import common, metadata_file, utils
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

    class MetadataFilenames:
        SINGLE_CELL_METADATA_FILE_NAME = "single_cell_metadata.tsv"
        SPATIAL_METADATA_FILE_NAME = "spatial_metadata.tsv"
        METADATA_ONLY_FILE_NAME = "metadata.tsv"

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

    OUTPUT_README_FILE_NAME = "README.md"

    README_ANNDATA_FILE_NAME = "readme_anndata.md"
    README_ANNDATA_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_FILE_NAME

    README_ANNDATA_MERGED_FILE_NAME = "readme_anndata_merged.md"
    README_ANNDATA_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_MERGED_FILE_NAME

    README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
    README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

    README_SINGLE_CELL_MERGED_FILE_NAME = "readme_single_cell_merged.md"
    README_SINGLE_CELL_MERGED_FILE_PATH = (
        common.OUTPUT_DATA_PATH / README_SINGLE_CELL_MERGED_FILE_NAME
    )

    README_METADATA_NAME = "readme_metadata_only.md"
    README_METADATA_PATH = common.OUTPUT_DATA_PATH / README_METADATA_NAME

    README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
    README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

    README_SPATIAL_FILE_NAME = "readme_spatial.md"
    README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

    README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
    README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
    README_TEMPLATE_ANNDATA_MERGED_FILE_PATH = README_TEMPLATE_PATH / "anndata_merged.md"
    README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
    README_TEMPLATE_SINGLE_CELL_MERGED_FILE_PATH = README_TEMPLATE_PATH / "single_cell_merged.md"
    README_TEMPLATE_METADATA_PATH = README_TEMPLATE_PATH / "metadata_only.md"
    README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
    README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"

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
        file_name_parts = ["_".join(sample.multiplexed_ids)]
        file_name_parts.extend(
            [download_config["modality"], download_config["format"], "METADATA.tsv"]
        )
        return common.OUTPUT_DATA_PATH / "_".join(file_name_parts)

    @classmethod
    def get_readme_from_download_config(cls, download_config: Dict):
        match download_config:
            case {"metadata_only": True}:
                return cls.README_METADATA_PATH
            case {"excludes_multiplexed": False}:
                return cls.README_MULTIPLEXED_FILE_PATH
            case {"format": "ANN_DATA", "includes_merged": True}:
                return cls.README_ANNDATA_MERGED_FILE_PATH
            case {"modality": "SINGLE_CELL", "includes_merged": True}:
                return cls.README_SINGLE_CELL_MERGED_FILE_PATH
            case {"format": "ANN_DATA"}:
                return cls.README_ANNDATA_FILE_PATH
            case {"modality": "SINGLE_CELL"}:
                return cls.README_SINGLE_CELL_FILE_PATH
            case {"modality": "SPATIAL"}:
                return cls.README_SPATIAL_FILE_PATH

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
            lib for library in libraries for lib in library.get_combined_library_metadata()
        ]
        local_metadata_path = ComputedFile.get_local_project_metadata_path(project, download_config)
        metadata_file.write_metadata_dicts(libraries_metadata, local_metadata_path)

        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        project_data_file_paths = project.get_download_config_file_paths(download_config)

        zip_file_path = common.OUTPUT_DATA_PATH / computed_file_name
        with ZipFile(zip_file_path, "w") as zip_file:
            # Readme file
            zip_file.write(
                ComputedFile.get_readme_from_download_config(download_config),
                cls.OUTPUT_README_FILE_NAME,
            )
            # Metadata file
            output_file_constant = (
                f'{download_config["modality"]}_METADATA_FILE_NAME'
                if not download_config["metadata_only"]
                else "METADATA_ONLY_FILE_NAME"
            )
            zip_file.write(
                local_metadata_path, getattr(cls.MetadataFilenames, output_file_constant)
            )

            if not download_config.get("metadata_only", False):
                for file_path in library_data_file_paths:
                    output_path = file_path.relative_to(f"{project.scpca_id}/")
                    # Swap delimiter in multiplexed sample libraries from comma to underscore
                    if "," in file_path.parent.name:
                        new_delimiter_dir = Path("_".join(file_path.parent.name.split(",")))
                        output_path = new_delimiter_dir / file_path.name
                    zip_file.write(Library.get_local_file_path(file_path), output_path)

                for file_path in project_data_file_paths:
                    if "bulk" in file_path.name and download_config["modality"] == "SPATIAL":
                        continue
                    output_path = file_path.relative_to(f"{project.scpca_id}/")
                    zip_file.write(Library.get_local_file_path(file_path), output_path)
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
                download_config["modality"] == "SINGLE_CELL" and project.has_bulk_rna_seq
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

        computed_file.save()

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
            lib for library in libraries for lib in library.get_combined_library_metadata()
        ]
        local_metadata_path = ComputedFile.get_local_sample_metadata_path(sample, download_config)
        metadata_file.write_metadata_dicts(libraries_metadata, local_metadata_path)

        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        zip_file_path = common.OUTPUT_DATA_PATH / computed_file_name
        # This lock is primarily for multiplex. We added it here as a patch to keep things generic.
        with lock:  # It should be removed later for a cleaner solution.
            if not zip_file_path.exists():
                with ZipFile(zip_file_path, "w") as zip_file:
                    # Readme file
                    zip_file.write(
                        ComputedFile.get_readme_from_download_config(download_config),
                        cls.OUTPUT_README_FILE_NAME,
                    )

                    # Metadata file
                    zip_file.write(
                        local_metadata_path,
                        getattr(
                            cls.MetadataFilenames,
                            f'{download_config["modality"]}_METADATA_FILE_NAME',
                        ),
                    )

                    for file_path in library_data_file_paths:
                        output_path = file_path.relative_to(
                            f"{sample.project.scpca_id}/{','.join(sample.multiplexed_ids)}/"
                        )
                        zip_file.write(Library.get_local_file_path(file_path), output_path)

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

        computed_file.save()

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
        """Uploads the computed file to S3 using AWS CLI tool."""

        logger.info(f"Uploading {self}")
        subprocess.check_call(
            (
                "aws",
                "s3",
                "cp",
                str(self.zip_file_path),
                f"s3://{settings.AWS_S3_BUCKET_NAME}/{self.s3_key}",
            )
        )

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

    def process_computed_file(self, clean_up_output_data, update_s3):
        """Processes saving, upload and cleanup of a single computed file."""
        self.save()
        if update_s3:
            self.upload_s3_file()

        # Don't clean up multiplexed sample zips until the project is done
        is_multiplexed_sample = self.sample and self.sample.has_multiplexed_data

        if clean_up_output_data and not is_multiplexed_sample:
            self.zip_file_path.unlink(missing_ok=True)
