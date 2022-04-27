import os

from django.conf import settings
from django.db import models

import boto3
from botocore.client import Config

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class ComputedFile(models.Model):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    class FileNames:
        SINGLE_CELL_METADATA_FILE_NAME = "single_cell_metadata.tsv"
        SPATIAL_METADATA_FILE_NAME = "spatial_metadata.tsv"

    class FileTypes:
        PROJECT_SPATIAL_ZIP = "PROJECT_SPATIAL_ZIP"
        PROJECT_ZIP = "PROJECT_ZIP"
        SAMPLE_SPATIAL_ZIP = "SAMPLE_SPATIAL_ZIP"
        SAMPLE_ZIP = "SAMPLE_ZIP"

        CHOICES = (
            (PROJECT_SPATIAL_ZIP, "Project Spatial ZIP"),
            (PROJECT_ZIP, "Project ZIP"),
            (SAMPLE_SPATIAL_ZIP, "Sample Spatial ZIP"),
            (SAMPLE_ZIP, "Sample ZIP"),
        )

    README_FILE_NAME = "README.md"
    README_FILE_PATH = os.path.join(common.OUTPUT_DATA_DIR, README_FILE_NAME)
    README_TEMPLATE_FILE_PATH = os.path.join(common.TEMPLATE_DIR, "readme.md")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    s3_bucket = models.TextField(null=False)
    s3_key = models.TextField(null=False)
    size_in_bytes = models.BigIntegerField()
    type = models.TextField(choices=FileTypes.CHOICES)
    workflow_version = models.TextField(null=False)

    # This is going to be renamed to `project` later.
    prjct = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, related_name="project_computed_file"
    )

    # This is going to be renamed to `sample` later.
    smpl = models.ForeignKey(
        "Sample", null=True, on_delete=models.CASCADE, related_name="sample_computed_file"
    )

    @property
    def is_project_zip(self):
        return self.type == ComputedFile.FileTypes.PROJECT_ZIP

    @property
    def is_project_spatial_zip(self):
        return self.type == ComputedFile.FileTypes.PROJECT_SPATIAL_ZIP

    @property
    def download_url(self):
        """ A temporary URL from which the file can be downloaded. """
        return self.create_download_url()

    @property
    def metadata_file_name(self):
        if self.is_project_zip:
            return ComputedFile.FileNames.SINGLE_CELL_METADATA_FILE_NAME
        elif self.is_project_spatial_zip:
            return ComputedFile.FileNames.SPATIAL_METADATA_FILE_NAME

    @property
    def zip_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, self.s3_key)

    def create_download_url(self):
        """Create a temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            return s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.s3_bucket, "Key": self.s3_key},
                ExpiresIn=(60 * 60 * 24 * 7),  # 7 days in seconds.
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
