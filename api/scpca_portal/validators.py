import re
from typing import Any, Dict, List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
)

from scpca_portal.enums.modalities import Modalities

PROJECT_ID_REGEX = r"^SCPCP\d{6}$"
SAMPLE_ID_REGEX = r"^SCPCS\d{6}$"


class ProjectData(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)

    includes_bulk: bool = Field(default=True)
    single_cell: List[str] | str = Field(default_factory=list, alias=Modalities.SINGLE_CELL.value)
    spatial: List[str] = Field(default_factory=list, alias=Modalities.SPATIAL.value)

    @field_validator("single_cell", "spatial", mode="after")
    @classmethod
    def validate_samples_ids(cls, modality_value: Any, info: ValidationInfo):
        # Note: There's no actual need to check if field_name is "single_cell"
        # because if a str is passed to the "spatial" field, pydantic type checking will catch it.
        # The check is included here for extra clarity.
        if info.field_name == "single_cell" and isinstance(modality_value, str):
            if modality_value == "MERGED":
                return modality_value
            # TODO: add custom exception
            raise ValueError(
                """
                Invalid string value for 'single-cell' modality: {modality_value}.
                Only valid value is 'MERGED'.
                """
            )

        for sample_id in modality_value:
            if not re.match(SAMPLE_ID_REGEX, sample_id):
                # TODO: add custom exception
                raise ValueError(f"Invalid sample ID format: {sample_id}.")

        return modality_value


class DatasetData(RootModel):
    root: Dict[str, ProjectData]

    @model_validator(mode="after")
    @classmethod
    def validate_project_ids(cls, instance):
        for project_id in instance.root:
            if not re.match(PROJECT_ID_REGEX, project_id):
                # TODO: add custom exception
                raise ValueError(f"Invalid project ID format: {project_id}")
        return instance
