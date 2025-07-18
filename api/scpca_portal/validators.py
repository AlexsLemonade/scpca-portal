import re
from typing import Any, Dict, Iterable, List

from pydantic import BaseModel, Field, ValidationInfo, field_validator

PROJECT_ID_REGEX = r"^SCPCP\d{6}$"
SAMPLE_ID_REGEX = r"^SCPCS\d{6}$"


class ProjectData(BaseModel):
    includes_bulk: bool = Field(default=True)
    single_cell: List[str] | str = Field(default_factory=list)
    spatial: List[str] = Field(default_factory=list)

    @field_validator("single_cell", "spatial", mode="after")
    @classmethod
    def validate_samples_ids(cls, value: Any, info: ValidationInfo):
        if info.field_name == "single_cell" and isinstance(value, str) and value == "MERGED":
            return value

        if not isinstance(value, list):
            raise TypeError(
                "Expected a list of Sample IDs or a 'MERGED' string (for single-cell only)."
            )

        for sample_id in value:
            if not re.match(SAMPLE_ID_REGEX, sample_id):
                raise ValueError(f"Invalid sample ID: {sample_id}.")

        return value


class DatasetData(BaseModel):
    projects_data: Dict[str, ProjectData]
    # __root__: Dict[str, ProjectData]  # alternative to projects_data declaration approach

    @field_validator("projects_data", mode="after")
    @classmethod
    def validate_project_ids(cls, values: Iterable[Any]):
        for project_id in values:
            if not re.match(PROJECT_ID_REGEX, project_id):
                raise ValueError(f"Invalid project ID: {project_id}")
        return values
