import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator, model_validator

from scpca_portal.enums import Modalities
from scpca_portal.exceptions import (
    DatasetDataInvalidModalityStringError,
    DatasetDataInvalidProjectIDError,
    DatasetDataInvalidSampleIDError,
    DatasetDataInvalidSampleIDLocationError,
    DatasetDataProjectsDontExistError,
    DatasetDataProjectsNoBulkDataError,
    DatasetDataProjectsNoMergedFilesError,
    DatasetDataSampleAssociationsError,
    DatasetDataSamplesDontExistError,
)
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
                raise DatasetDataInvalidSampleIDLocationError

            if modality_value == "MERGED":
                return modality_value

            raise DatasetDataInvalidModalityStringError(modality_value)

        for sample_id in modality_value:
            if not re.match(SAMPLE_ID_REGEX, sample_id):
                raise DatasetDataInvalidSampleIDError(sample_id)
        return modality_value


class DatasetDataModel(RootModel):
    root: Dict[str, ProjectDataModel]

    @model_validator(mode="after")
    def validate_project_ids(self):
        for project_id in self.root:
            if not re.match(PROJECT_ID_REGEX, project_id):
                raise DatasetDataInvalidProjectIDError(project_id)
        return self


class DatasetDataModelRelations:
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict:
        DatasetDataModelRelations.validate_projects(data)
        DatasetDataModelRelations.validate_samples(data)
        return data

    @staticmethod
    def validate_projects(data: Dict[str, Any]):
        """
        Validates that projects set in the data attribute
        both exist and have the requested project level data (bulk and merged)
        Raises exceptions if projects and the requested data do not exist.
        """

        # validate that all projects exist
        existing_projects = Project.objects.filter(scpca_id__in=data.keys())
        existing_project_ids = existing_projects.values_list("scpca_id", flat=True)
        if invalid_project_ids := set(data.keys()) - set(existing_project_ids):
            raise DatasetDataProjectsDontExistError(invalid_project_ids)

        # validate that requested merged projects have merged data
        invalid_merged_ids = []
        for project in existing_projects:
            if data.get(project.scpca_id, {}).get(Modalities.SINGLE_CELL) == "MERGED":
                if not (project.includes_merged_anndata or project.includes_merged_sce):
                    invalid_merged_ids.append(project.scpca_id)
        if invalid_merged_ids:
            raise DatasetDataProjectsNoMergedFilesError(invalid_merged_ids)

        # validate that projects have requested bulk data
        invalid_merged_ids = []
        if invalid_bulk_ids := [
            project.scpca_id
            for project in existing_projects
            if data.get(project.scpca_id, {}).get("includes_bulk") and not project.has_bulk_rna_seq
        ]:
            raise DatasetDataProjectsNoBulkDataError(invalid_bulk_ids)

    @staticmethod
    def validate_samples(data: Dict[str, Any]):
        """
        Validates that samples set into the data attribute,
        both exist and are correctly related with their projects.
        Raises exceptions if projects, samples or their associations do not exist.
        """

        existing_project_ids = Project.objects.filter(scpca_id__in=data.keys()).values_list(
            "scpca_id", flat=True
        )

        # validate that all samples exist
        data_sample_ids = [
            sample_id
            for project_data in data.values()
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]
            for sample_id in project_data[modality]
            if re.match(SAMPLE_ID_REGEX, sample_id)  # don't iterate over the "MERGED" string
        ]
        existing_samples = Sample.objects.filter(scpca_id__in=data_sample_ids).values(
            "scpca_id", "project__scpca_id", "has_single_cell_data", "has_spatial_data"
        )
        existing_sample_ids = [sample["scpca_id"] for sample in existing_samples]
        if invalid_sample_ids := set(data_sample_ids) - set(existing_sample_ids):
            raise DatasetDataSamplesDontExistError(invalid_sample_ids)

        # validate that existing samples were put with their associated projects and modalities
        existing_project_modality_sample_ids = {
            project_id: {Modalities.SINGLE_CELL: [], Modalities.SPATIAL: []}
            for project_id in existing_project_ids
        }

        # populate existing sample ids dict
        for sample in existing_samples:
            project_id = sample["project__scpca_id"]
            # this is the case when the project exists
            # but the samples are applied to the wrong project
            if project_id not in existing_project_modality_sample_ids:
                continue

            if sample["has_single_cell_data"]:
                existing_project_modality_sample_ids[project_id][
                    Modalities.SINGLE_CELL.value
                ].append(sample["scpca_id"])

            if sample["has_spatial_data"]:
                existing_project_modality_sample_ids[project_id][Modalities.SPATIAL.value].append(
                    sample["scpca_id"]
                )

        for project_id, project_data in data.items():
            for modality in [Modalities.SINGLE_CELL, Modalities.SPATIAL]:
                if project_data[modality] == "MERGED":
                    continue

                data_modality_sample_ids = project_data[modality]
                if invalid_sample_ids := set(data_modality_sample_ids) - set(
                    existing_project_modality_sample_ids[project_id][modality]
                ):
                    raise DatasetDataSampleAssociationsError(
                        project_id, modality, invalid_sample_ids
                    )
