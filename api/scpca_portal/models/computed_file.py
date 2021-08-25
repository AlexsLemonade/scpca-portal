from django.db import models

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel


class ComputedFile(SafeDeleteModel):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    objects = SafeDeleteManager()
    deleted_objects = SafeDeleteDeletedManager()
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    type = models.TextField(null=False)
    workflow_version = models.TextField(null=False)
    s3_bucket = models.TextField(null=False)
    s3_key = models.TextField(null=False)

    is_deleted = models.BooleanField(default=False)

    @property
    def download_url(self):
        """ A temporary URL from which the file can be downloaded.

        TODO: implement this
        https://github.com/AlexsLemonade/scpca-portal/issues/14
        """
        return f"https://{self.s3_bucket}.s3.amazonaws.com/{self.s3_key}"
