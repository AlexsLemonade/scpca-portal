import uuid
from typing import Any, Dict, List

from django.db import models

from scpca_portal import common
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models import APIToken, ComputedFile
from scpca_portal.models.base import TimestampedModel


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

    # Non user-editable - set during processing
    started_at = models.DateTimeField(null=True)
    is_started = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True)
    is_processed = models.BooleanField(default=False)
    errored_at = models.DateTimeField(null=True)
    is_errored = models.BooleanField(default=False)
    error_message = models.TextField(null=True)
    expires_at = models.DateTimeField(null=True)
    is_expired = models.BooleanField(default=False)  # Set by cronjob

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

    @staticmethod
    def validate_data(json_obj: Dict) -> bool:
        data_validator = DataValidator(json_obj)
        return data_validator.is_valid


class DataValidator:
    def __init__(self, data: Dict[str, Dict]) -> None:
        self.data: Dict[str, Dict[str, Any]] = data

    @property
    def is_valid(self) -> bool:
        return all(self.validate_project(project_id) for project_id in self.data.keys())

    def validate_project(self, project_id: str) -> bool:
        is_valid = self._validate_project_id(project_id)
        is_valid &= (
            self._validate_merge_single_cell(project_id)
            if self.data.get(project_id).get("merge_single_cell")
            else True
        )
        is_valid &= (
            self._validate_includes_bulk(project_id)
            if self.data.get(project_id).get("includes_bulk")
            else True
        )
        is_valid &= (
            self._validate_single_cell(project_id)
            if self.data.get(project_id).get(Modalities.SINGLE_CELL)
            else True
        )
        is_valid &= (
            self._validate_spatial(project_id)
            if self.data.get(project_id).get(Modalities.SPATIAL)
            else True
        )

        return is_valid

    def _validate_project_id(self, project_id):
        return self._validate_resource_id(project_id, common.PROJECT_ID_PREFIX)

    def _validate_resource_id(self, resource_id: str, resource_prefix: str) -> bool:
        if not isinstance(resource_id, str):
            return False

        if not resource_id.startswith(resource_prefix):
            return False

        resource_id_number = resource_id.removeprefix(resource_prefix)
        return len(resource_id_number) == 6 and resource_id_number.isdigit()

    def _validate_merge_single_cell(self, project_id) -> bool:
        return isinstance(self.data.get(project_id).get("merge_single_cell"), bool)

    def _validate_includes_bulk(self, project_id) -> bool:
        return isinstance(self.data.get(project_id).get("includes_bulk"), bool)

    def _validate_single_cell(self, project_id) -> bool:
        return self._validate_modality(self.data.get(project_id).get(Modalities.SINGLE_CELL))

    def _validate_spatial(self, project_id) -> bool:
        return self._validate_modality(self.data.get(project_id).get(Modalities.SPATIAL))

    def _validate_modality(self, modality_sample_ids: List) -> bool:
        if not isinstance(modality_sample_ids, list):
            return False

        for sample_id in modality_sample_ids:
            if not self._validate_resource_id(sample_id, common.SAMPLE_ID_PREFIX):
                return False

        return True
