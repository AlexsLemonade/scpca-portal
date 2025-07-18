import re
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

PROJECT_ID_REGEX = r"^SCPCP\d{6}$"
SAMPLE_ID_REGEX = r"^SCPCS\d{6}$"


class ProjectData(BaseModel):
    includes_bulk: Optional[bool] = None
    single_cell: Optional[Union[List[str], str]] = Field(default=None, alias="single_cell")
    spatial: Optional[List[str]] = Field(default=None, alias="spatial")

    @validator("single_cell", "spatial", each_item=True)
    def validate_samples_ids(cls, value):
        if not re.match(SAMPLE_ID_REGEX, value):
            raise ValueError(f"Invalid sample ID: {value}")


class DatasetData(BaseModel):
    __root__: Dict[str, ProjectData]

    @root_validator(pre=True)
    def validate_project_ids(cls, values):
        for project_id in values:
            if not re.match(PROJECT_ID_REGEX, project_id):
                raise ValueError(f"Invalid project ID: {project_id}")
        return values
