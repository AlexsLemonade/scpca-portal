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
    def validate_project_ids(self):
        for project_id in self.root:
            if not re.match(PROJECT_ID_REGEX, project_id):
                # TODO: add custom exception
                raise ValueError(f"Invalid project ID format: {project_id}")
        return self

    @model_validator(mode="after")
    def validate_anndata_has_no_spatial_data(self, info: ValidationInfo):
        if info.context and info.context.get("format") == DatasetFormats.ANN_DATA.value:
            if invalid_project_ids := [
                project_id for project_id, project_data in self.root.items() if project_data.SPATIAL
            ]:
                raise ValueError(
                    "Datasets with format ANN_DATA "
                    "do not support projects with SPATIAL samples. "
                    f"Invalid projects: {', '.join(sorted(invalid_project_ids))}"
                )

        return self


class DatasetDataModelRelations:

    @staticmethod
    def validate(data: Dict[str, Any], format) -> Dict:
        """
        Validates that projects and samples passed into the data attribute,
        both exist and are correctly related.
        Raises exceptions if projects, samples or their associations do not exist.
        """
        # validate that all projects exist
        existing_projects = Project.objects.filter(scpca_id__in=data.keys())
        existing_project_ids = existing_projects.values_list("scpca_id", flat=True)
        if invalid_project_ids := set(data.keys()) - set(existing_project_ids):
            # TODO: add custom exception
            raise Exception(
                f"The following projects do not exist: {', '.join(sorted(invalid_project_ids ))}"
            )

        # validate that requested merged projects have merged data
        invalid_merged_ids = []
        for project in existing_projects:
            if data.get(project.scpca_id, {}).get(Modalities.SINGLE_CELL) == "MERGED":
                if (format == DatasetFormats.ANN_DATA and project.includes_merged_anndata) or (
                    format == DatasetFormats.SINGLE_CELL_EXPERIMENT and project.includes_merged_sce
                ):
                    invalid_merged_ids.append(project.scpca_id)
        if invalid_merged_ids:
            # TODO: add custom exception
            raise Exception(
                "The following projects do not have merged files: "
                f"{', '.join(sorted(invalid_merged_ids))}"
            )

        # validate that projects have requested bulk data
        invalid_merged_ids = []
        if invalid_bulk_ids := [
            project.scpca_id
            for project in existing_projects
            if data.get(project.scpca_id, {}).get("includes_bulk") and project.has_bulk_rna_seq
        ]:
            # TODO: add custom exception
            raise Exception(
                "The following projects do not have bulk data: "
                f"{', '.join(sorted(invalid_bulk_ids))}"
            )

        # validate that all samples exist
        data_sample_ids = {
            sample_id
            for project_data in data.values()
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]
            for sample_id in project_data[modality]
            if re.match(SAMPLE_ID_REGEX, sample_id)  # don't iterate over the "MERGED" string
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
                        f"{', '.join(sorted(missing_keys))}"
                    )

        return data
