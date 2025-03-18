import uuid
from typing import Any, Dict, Iterable, List

from django.db import models

from typing_extensions import Self

from scpca_portal import common
from scpca_portal.enums import Configs, DatasetDataProjectConfig, DatasetFormats, Modalities
from scpca_portal.models.api_token import APIToken
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.project import Project
from scpca_portal.models.sample import Sample


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

    # Internally generated datasets
    is_ccdl = models.BooleanField(default=False)

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

    @classmethod
    def get_from_projects(cls, config: Configs, projects: Iterable[Project]) -> Self:
        download_config = common.DOWNLOAD_CONFIGS[config]

        data = {}
        for project in projects:
            samples = Sample.objects.filter(project__scpca_id=project.scpca_id)
            if download_config.get("excludes_multiplexed"):
                samples = samples.filter(has_multiplexed_data=False)

            data[project.scpca_id] = {
                "merge_single_cell": download_config.get("includes_merged"),
                "includes_bulk": True,
                Modalities.SINGLE_CELL: samples.filter(modality=Modalities.SINGLE_CELL).values_list(
                    "scpca_id", flat=True
                ),
                Modalities.SPATIAL: samples.filter(modality=Modalities.SPATIAL).values_list(
                    "scpca_id", flat=True
                ),
            }

        return cls(
            data=data,
            format=download_config.get("format"),
            is_ccdl=True,
        )

    @classmethod
    def get_from_sample(cls, config: Configs, sample: Sample) -> Self:
        download_config = common.DOWNLOAD_CONFIGS[config]
        project_config = {
            "merge_single_cell": False,
            "includes_bulk": False,
            Modalities.SINGLE_CELL: [],
            Modalities.SPATIAL: [],
        }
        match download_config.get("modality"):
            case Modalities.SINGLE_CELL:
                project_config[Modalities.SINGLE_CELL].append(sample.scpca_id)
            case Modalities.SPATIAL:
                project_config[Modalities.SPATIAL].append(sample.scpca_id)
            case _:
                raise ValueError(
                    "Invalid download config passed: Sample config must have a modality."
                )

        return cls(
            data={sample.project.scpca_id: project_config},
            is_metadata_only=False,
            format=download_config.get("modality"),
            is_ccdl=True,
        )

    @property
    def is_data_valid(self) -> bool:
        data_validator = DataValidator(self.data)
        return data_validator.is_valid


class DataValidator:
    def __init__(self, data: Dict[str, Dict]) -> None:
        self.data: Dict[str, Dict[str, Any]] = data

    @property
    def is_valid(self) -> bool:
        return all(self.validate_project(project_id) for project_id in self.data.keys())

    @property
    def valid_projects(self) -> List[str]:
        return [project_id for project_id in self.data.keys() if self.validate_project(project_id)]

    @property
    def invalid_projects(self) -> List[str]:
        return [
            project_id for project_id in self.data.keys() if not self.validate_project(project_id)
        ]

    def validate_project(self, project_id: str) -> bool:
        if not self._validate_project_id(project_id):
            return False

        if not self._validate_merge_single_cell(project_id):
            return False

        if not self._validate_includes_bulk(project_id):
            return False

        if not self._validate_single_cell(project_id):
            return False

        if not self._validate_spatial(project_id):
            return False

        return True

    def _validate_project_id(self, project_id):
        return self._validate_id(project_id, common.PROJECT_ID_PREFIX)

    def _validate_id(self, id: str, prefix: str) -> bool:
        if not isinstance(id, str):
            return False

        if not id.startswith(prefix):
            return False

        id_number = id.removeprefix(prefix)
        return len(id_number) == 6 and id_number.isdigit()

    def _validate_merge_single_cell(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.MERGE_SINGLE_CELL):
            return isinstance(value, bool)

        return True

    def _validate_includes_bulk(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.INCLUDES_BULK):
            return isinstance(value, bool)

        return True

    def _validate_single_cell(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.SINGLE_CELL):
            return self._validate_modality(value)

        return True

    def _validate_spatial(self, project_id) -> bool:
        if value := self.data.get(project_id, {}).get(DatasetDataProjectConfig.SPATIAL):
            return self._validate_modality(value)

        return True

    def _validate_modality(self, modality_sample_ids: List) -> bool:
        if not isinstance(modality_sample_ids, list):
            return False

        for sample_id in modality_sample_ids:
            if not self._validate_id(sample_id, common.SAMPLE_ID_PREFIX):
                return False

        return True
