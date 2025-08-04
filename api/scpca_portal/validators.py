import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator, model_validator

from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models.project import Project
from scpca_portal.models.sample import Sample

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
            if invalid_ids := [
                project_id
                for project_id, project_data in data.items()
                if project_data.get(Modalities.SPATIAL.value)
            ]:
                # TODO: add custom exception
                "The following projects requested Spatial data with an invalid format of ANNADATA:"
                raise Exception(
                    "The following projects requested Spatial data "
                    "with an invalid format of ANNDATA: "
                    f"{', '.join(sorted(invalid_ids))}"
                )

        # validate that all projects exist
        existing_project_ids = Project.objects.filter(scpca_id__in=data.keys()).values_list(
            "scpca_id", flat=True
        )
        if missing_keys := set(data.keys()) - set(existing_project_ids):
            # TODO: add custom exception
            raise Exception(
                f"The following projects do not exist: {', '.join(sorted(missing_keys))}"
            )

        # TODO add bulk check here

        # validate that all samples exist
        data_sample_ids = {
            sample_id
            for project_data in data.values()
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]
            for sample_id in project_data[modality]
        }
        data_samples = Sample.objects.filter(scpca_id__in=data_sample_ids).values(
            "scpca_id", "project__scpca_id", "has_single_cell_data", "has_spatial_data"
        )
        if missing_keys := data_sample_ids - {sample["scpca_id"] for sample in data_samples}:
            # TODO: add custom exception
            raise Exception(
                f"The following samples do not exist: {', '.join(sorted(missing_keys))}"
            )

        # validate that existing samples were put with their associated projects and modalities
        valid_project_modality_sample_ids = {
            project_id: {Modalities.SINGLE_CELL: [], Modalities.SPATIAL: []}
            for project_id in existing_project_ids
        }

        for sample in data_samples:
            project_id = sample["project__scpca_id"]

            if sample["has_single_cell_data"]:
                valid_project_modality_sample_ids[project_id][Modalities.SINGLE_CELL].append(
                    sample["scpca_id"]
                )

            if sample["has_spatial_data"]:
                valid_project_modality_sample_ids[project_id][Modalities.SPATIAL].append(
                    sample["scpca_id"]
                )

        for project_id, project_data in data.items():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]:
                existing_ids = project_data[modality]
                if missing_keys := set(existing_ids) - set(
                    valid_project_modality_sample_ids[project_id][modality]
                ):
                    # TODO: add custom exception
                    raise Exception(
                        "The following samples are not associated "
                        f"with {project_id} and {modality}: "
                        "{', '.join(sorted(missing_keys))}"
                    )

        return data
