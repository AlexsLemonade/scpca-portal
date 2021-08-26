from django.conf import settings
from django.db import models

import boto3
from botocore.client import Config

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class ComputedFile(models.Model):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    type = models.TextField(null=False)
    workflow_version = models.TextField(null=False)
    s3_bucket = models.TextField(null=False)
    s3_key = models.TextField(null=False)
    size_in_bytes = models.BigIntegerField()

    is_deleted = models.BooleanField(default=False)

    @property
    def download_url(self):
        """ A temporary URL from which the file can be downloaded.

        TODO: implement this
        https://github.com/AlexsLemonade/scpca-portal/issues/14
        """
        return f"https://{self.s3_bucket}.s3.amazonaws.com/{self.s3_key}"

    def delete_s3_file(self, force=False):
        # If we're not running in the cloud then we shouldn't try to
        # delete something from S3 unless force is set.
        if not settings.UPDATE_IMPORTED_DATA and not force:
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

        self.s3_key = None
        self.s3_bucket = None
        self.save()
        return True
