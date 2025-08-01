import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator, model_validator

from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models.project import Project

PROJECT_ID_REGEX = r"^SCPCP\d{6}$"
SAMPLE_ID_REGEX = r"^SCPCS\d{6}$"


class ProjectDataModel(BaseModel):
    includes_bulk: bool = Field(default=True)
    SINGLE_CELL: List[str] | str = Field(default_factory=list, alias=Modalities.SINGLE_CELL.value)
    SPATIAL: List[str] = Field(default_factory=list, alias=Modalities.SPATIAL.value)

    @field_validator(Modalities.SINGLE_CELL.value, Modalities.SPATIAL.value, mode="after")
    @classmethod
    def validate_samples_ids(cls, modality_value: Any, info: ValidationInfo):
        # Note: There's no actual need to check if field_name is "SINGLE_CELL"
        # because if a str is passed to the "SPATIAL" field, pydantic type checking will catch it.
        # The check is included here for extra clarity.
        if info.field_name == Modalities.SINGLE_CELL.value and isinstance(modality_value, str):
            if re.match(SAMPLE_ID_REGEX, modality_value):
                raise ValueError("Sample IDs must be inside an Array.")

            if modality_value == "MERGED":
                return modality_value

            # TODO: add custom exception
            raise ValueError(
                f"""
                Invalid string value for 'single-cell' modality: {modality_value}.
                Only valid value is 'MERGED'.
                """
            )

        for sample_id in modality_value:
            if not re.match(SAMPLE_ID_REGEX, sample_id):
                # TODO: add custom exception
                raise ValueError(f"Invalid sample ID format: {sample_id}.")

        return modality_value


class DatasetDataModel(RootModel):
    root: Dict[str, ProjectDataModel]

    @model_validator(mode="after")
    @classmethod
    def validate_project_ids(cls, instance):
        for project_id in instance.root:
            if not re.match(PROJECT_ID_REGEX, project_id):
                # TODO: add custom exception
                raise ValueError(f"Invalid project ID format: {project_id}")
        return instance


class DatasetDataResourceExistence:

    @staticmethod
    def validate(data: Dict[str, Any], format: DatasetFormats) -> Dict:
        """
        Validates that projects and samples passed into the data attribute,
        both exist and are correctly related.
        Raises exceptions if projects, samples or their associations do not exist.
        """
        if format == DatasetFormats.ANN_DATA.value:
            if any(
                project_data.get(Modalities.SPATIAL.value, []) for project_data in data.values()
            ):
                # TODO: add custom exception
                raise Exception("No Spatial data for ANNDATA.")

        # validate that all projects exist
        existing_ids = Project.objects.filter(scpca_id__in=data.keys()).values_list(
            "scpca_id", flat=True
        )
        if missing_keys := set(data.keys()) - set(existing_ids):
            raise Exception(f"The following projects do not exist: {list(missing_keys)}")

        # TODO: sample modality existence check
        return data
