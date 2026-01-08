from typing import Dict, List

from django.db import models

from typing_extensions import Self

from scpca_portal import ccdl_datasets, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import CCDLDatasetNames, Modalities
from scpca_portal.models.datasets import DatasetABC
from scpca_portal.models.project import Project

logger = get_and_configure_logger(__name__)


class CCDLDataset(DatasetABC):
    class Meta:
        db_table = "ccdl_datasets"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    ccdl_name = models.TextField(choices=CCDLDatasetNames.choices, null=True)
    ccdl_project_id = models.TextField(null=True)
    ccdl_modality = models.TextField(choices=Modalities.choices, null=True)

    def __str__(self):
        return (
            f"CCDL Dataset {self.id}: "
            f"{self.ccdl_project_id if self.ccdl_project_id else 'PORTAL WIDE'} {self.ccdl_name}"
        )

    @classmethod
    def get_or_find_ccdl_dataset(
        cls, ccdl_name: CCDLDatasetNames, project_id: str | None = None
    ) -> tuple[Self, bool]:
        if dataset := cls.objects.filter(
            is_ccdl=True, ccdl_name=ccdl_name, ccdl_project_id=project_id
        ).first():
            return dataset, True

        dataset = cls(ccdl_name=ccdl_name, ccdl_project_id=project_id)
        dataset.ccdl_modality = dataset.ccdl_type["modality"]
        dataset.format = dataset.ccdl_type["format"]
        dataset.data = dataset.get_ccdl_data()
        return dataset, False

    def get_ccdl_data(self) -> Dict:
        projects = Project.objects.all()
        if self.ccdl_project_id:
            projects = projects.filter(scpca_id=self.ccdl_project_id)

        data = {}
        for project in projects:
            samples = project.samples.all()
            if self.ccdl_type.get("excludes_multiplexed"):
                samples = samples.filter(has_multiplexed_data=False)

            modality = self.ccdl_type.get("modality")
            # don't add projects to data attribute that don't have data
            if modality and not samples.filter(libraries__modality=modality).exists():
                continue

            data[project.scpca_id] = {
                # single cell modality files get bulk, but not spatial and all metadata files
                "includes_bulk": modality == Modalities.SINGLE_CELL,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: [],
            }

            single_cell_sample_ids = samples.filter(
                libraries__modality=Modalities.SINGLE_CELL
            ).values_list("scpca_id", flat=True)
            spatial_sample_ids = samples.filter(libraries__modality=Modalities.SPATIAL).values_list(
                "scpca_id", flat=True
            )

            match modality:
                case Modalities.SINGLE_CELL:
                    data[project.scpca_id][modality] = (
                        list(single_cell_sample_ids)
                        if not self.ccdl_type.get("includes_merged")
                        else "MERGED"
                    )
                case Modalities.SPATIAL:
                    data[project.scpca_id][modality] = list(spatial_sample_ids)
                case _:  # All metadata case
                    data[project.scpca_id][Modalities.SINGLE_CELL] = list(single_cell_sample_ids)
                    data[project.scpca_id][Modalities.SPATIAL] = list(spatial_sample_ids)
        return data

    @property
    def ccdl_type(self) -> Dict:
        return ccdl_datasets.TYPES.get(self.ccdl_name, {})

    @property
    def is_valid_ccdl_dataset(self) -> bool:
        if not self.ccdl_project_id and self.ccdl_name not in ccdl_datasets.PORTAL_TYPE_NAMES:
            return False

        if not self.libraries.exists():
            return False

        return self.projects.filter(**self.ccdl_type.get("constraints", {})).exists()

    @classmethod
    def create_or_update_ccdl_datasets(
        cls, *, ignore_hash: bool = False
    ) -> tuple[List[Self], List[Self]]:
        """
        Iterates over all possible project and portal wide ccdl datasets,
        and creates or updates and susequently returns the valid ones.
        """
        ccdl_project_ids = list(Project.objects.values_list("scpca_id", flat=True))
        portal_wide_ccdl_project_id = None
        dataset_ccdl_project_ids = [*ccdl_project_ids, portal_wide_ccdl_project_id]

        created_datasets = []
        updated_datasets = []
        for ccdl_name in ccdl_datasets.TYPES:
            for ccdl_project_id in dataset_ccdl_project_ids:
                dataset, found = cls.get_or_find_ccdl_dataset(ccdl_name, ccdl_project_id)

                if found:
                    dataset.data = dataset.get_ccdl_data()
                    if dataset.is_hash_unchanged and not ignore_hash:
                        continue
                    updated_datasets.append(dataset)
                else:
                    if not dataset.is_valid_ccdl_dataset:
                        continue
                    created_datasets.append(dataset)

                # TODO: This should be optimized with bulk create and bulk update.
                # This can be accomplished by adding a custom manager which implements custom
                # bulk_create and bulk_update methods that preserve the cached attrs saving logic.
                dataset.save()

        return created_datasets, updated_datasets

    @property
    def download_filename(self) -> str:
        # CCDL Datasets have a default DatasetFormat of SINGLE_CELL_EXERPIMENT,
        # though many of their files are of FileFormat SPATIAL_SPACERANGER.
        # CCDL Spatial Datasets should have an output_format of "spaceranger".
        output_format = "-".join(self.format.split("_")).lower()
        if self.ccdl_modality == Modalities.SPATIAL:
            output_format = "spaceranger"

        date = utils.get_today_string()

        if not self.ccdl_project_id:
            return f"portal-wide_{output_format}_{date}.zip"

        return f"{self.ccdl_project_id}_{output_format}_{date}.zip"

    @property
    def download_url(self) -> str | None:
        """A temporary URL from which the file can be downloaded."""
        if not self.computed_file:
            return None

        return self.computed_file.get_dataset_download_url(self.download_filename)
