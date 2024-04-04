import subprocess
from pathlib import Path
from zipfile import ZipFile

from django.conf import settings
from django.db import models

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel

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

    # TODO(ark): these values are redundant and need to be refactored in order not to violate DRY.
    class OutputFileModalities:
        MULTIPLEXED = "MULTIPLEXED"
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (MULTIPLEXED, "Multiplexed"),
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    class OutputFileTypes:
        PROJECT_MULTIPLEXED_ZIP = "PROJECT_MULTIPLEXED_ZIP"
        PROJECT_SPATIAL_ZIP = "PROJECT_SPATIAL_ZIP"
        PROJECT_ZIP = "PROJECT_ZIP"

        SAMPLE_MULTIPLEXED_ZIP = "SAMPLE_MULTIPLEXED_ZIP"
        SAMPLE_SPATIAL_ZIP = "SAMPLE_SPATIAL_ZIP"
        SAMPLE_ZIP = "SAMPLE_ZIP"

        CHOICES = (
            (PROJECT_MULTIPLEXED_ZIP, "Project Multiplexed ZIP"),
            (PROJECT_SPATIAL_ZIP, "Project Spatial ZIP"),
            (PROJECT_ZIP, "Project ZIP"),
            (SAMPLE_MULTIPLEXED_ZIP, "Sample Multiplexed ZIP"),
            (SAMPLE_SPATIAL_ZIP, "Sample Spatial ZIP"),
            (SAMPLE_ZIP, "Sample ZIP"),
        )

    class OutputFileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        )

    format = models.TextField(choices=OutputFileFormats.CHOICES)
    modality = models.TextField(choices=OutputFileModalities.CHOICES)
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    type = models.TextField(choices=OutputFileTypes.CHOICES)
    workflow_version = models.TextField()

    project = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, related_name="project_computed_files"
    )
    sample = models.ForeignKey(
        "Sample", null=True, on_delete=models.CASCADE, related_name="sample_computed_files"
    )

    def __str__(self):
        return (
            f"'{self.project or self.sample}' {dict(self.OutputFileFormats.CHOICES)[self.format]} "
            f"computed file ({self.size_in_bytes}B)"
        )

    @property
    def is_project_multiplexed_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP

    @property
    def is_project_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_ZIP

    @property
    def is_project_spatial_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_SPATIAL_ZIP

    @property
    def metadata_file_name(self):
        if self.is_project_multiplexed_zip or self.is_project_zip:
            return ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
        if self.is_project_spatial_zip:
            return ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME

    # TODO: this method is not used elsewhere in the codebase
    @property
    def download_url(self):
        """A temporary URL from which the file can be downloaded."""
        return self.create_download_url()

