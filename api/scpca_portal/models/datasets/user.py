from collections import Counter, defaultdict
from typing import Any, Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models.datasets.base import DatasetABC
from scpca_portal.models.project import Project
from scpca_portal.validators import DatasetDataModel, DatasetDataModelRelations

logger = get_and_configure_logger(__name__)


class UserDataset(DatasetABC):
    class Meta:
        db_table = "user_datasets"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    # Cached File Attrs
    total_sample_count = models.BigIntegerField(default=0)
    diagnoses_summary = models.JSONField(default=dict)
    files_summary = models.JSONField(default=list)  # expects a list of dicts
    project_diagnoses = models.JSONField(default=dict)
    project_modality_counts = models.JSONField(default=dict)
    modality_count_mismatch_projects = ArrayField(models.TextField(), default=list)
    project_sample_counts = models.JSONField(default=dict)
    project_titles = models.JSONField(default=dict)

    def __str__(self):
        return f"User Dataset {self.id}"

    # INSTANCE CREATION AND MODIFICATION
    def save(self, *args, **kwargs):
        """
        In addition to the built-in object saving functionality,
        cached attributes should be re-computed and re-assigned on each save.
        """

        # stats property attributes
        self.total_sample_count = self.get_total_sample_count()
        self.diagnoses_summary = self.get_diagnoses_summary()
        self.files_summary = self.get_files_summary()
        self.project_diagnoses = self.get_project_diagnoses()
        self.project_modality_counts = self.get_project_modality_counts()
        self.modality_count_mismatch_projects = self.get_modality_count_mismatch_projects()
        self.project_sample_counts = self.get_project_sample_counts()
        self.project_titles = self.get_project_titles()

        super().save(*args, **kwargs)

    @staticmethod
    def validate_data(data: Dict[str, Any], format: DatasetFormats) -> Dict:
        structured_data = DatasetDataModel.model_validate(
            data, context={"format": format}
        ).model_dump()
        validated_data = DatasetDataModelRelations.validate(structured_data)

        return validated_data

    # CACHED ATTRIBUTES LOGIC
    def get_total_sample_count(self) -> int:
        """
        Returns the total number of unique samples in data attribute across all project modalities.
        """
        all_samples = (
            self.get_selected_samples([Modalities.SINGLE_CELL, Modalities.SPATIAL])
            .distinct()
            .values_list("scpca_id", flat=True)
        )

        return all_samples.count()

    def get_diagnoses_summary(self) -> dict:
        """
        Counts present all diagnoses for samples (excluding bulk) in datasets.
        Returns dict where key is the diagnosis and value is a dict
        of project and sample counts.
        """
        samples = self.get_selected_samples([Modalities.SINGLE_CELL, Modalities.SPATIAL])

        # all diagnoses in the dataset
        if (
            diagnoses := samples.values("diagnosis")
            .annotate(
                samples=Count("scpca_id"),
                projects=Count("project_id", distinct=True),
            )
            .order_by("diagnosis")
        ):
            return {d.pop("diagnosis"): d for d in diagnoses}

        return {}

    def get_files_summary(self) -> list[dict]:
        """
        Iterates over pre-defined file types that will be present in the dataset download.
        This break down looks at the type of information present in the individual files as well.
        Returns a list of dicts with name, samples_count, and format as keys.
        """
        single_cell_samples = self.get_selected_samples([Modalities.SINGLE_CELL])
        single_cell_libraries = self.libraries.filter(modality=Modalities.SINGLE_CELL)
        spatial_samples = self.get_selected_samples([Modalities.SPATIAL])
        spatial_libraries = self.libraries.filter(modality=Modalities.SPATIAL)
        bulk_samples = self.get_selected_samples([Modalities.BULK_RNA_SEQ])
        bulk_libraries = self.libraries.filter(modality=Modalities.BULK_RNA_SEQ)

        summary_queries = [
            {
                "name": "Single-cell samples",
                "exclude": [
                    {"is_multiplexed": True},
                    {"metadata__seq_unit": "nucleus"},
                    {"has_cite_seq_data": True},
                ],
                "samples": single_cell_samples,
                "libraries": single_cell_libraries,
            },
            {
                "name": "Single-nuclei samples",
                "filter": {"metadata__seq_unit": "nucleus"},
                "exclude": [{"is_multiplexed": True}, {"has_cite_seq_data": True}],
                "samples": single_cell_samples,
                "libraries": single_cell_libraries,
            },
            {
                "name": "Single-cell samples with CITE-seq",
                "filter": {"has_cite_seq_data": True},
                "exclude": [{"is_multiplexed": True}, {"metadata__seq_unit": "nucleus"}],
                "samples": single_cell_samples,
                "libraries": single_cell_libraries,
            },
            {
                "name": "Single-cell multiplexed samples",
                "filter": {"is_multiplexed": True},
                "exclude": [{"metadata__seq_unit": "nucleus"}, {"has_cite_seq_data": True}],
                "samples": single_cell_samples,
                "libraries": single_cell_libraries,
            },
            {
                "name": "Single-nuclei multiplexed samples",
                "filter": {"is_multiplexed": True, "metadata__seq_unit": "nucleus"},
                "exclude": [{"has_cite_seq_data": True}],
                "samples": single_cell_samples,
                "libraries": single_cell_libraries,
            },
            {
                "name": "Spatial samples",
                "format": "Spaceranger",
                "samples": spatial_samples,
                "libraries": spatial_libraries,
            },
            {
                "name": "Bulk RNA-seq samples",
                "format": ".tsv",
                "samples": bulk_samples,
                "libraries": bulk_libraries,
            },
        ]

        summaries = []

        for query in summary_queries:
            libraries = query["libraries"].filter(**query.get("filter", {}))

            for exclude in query.get("exclude", []):
                libraries = libraries.exclude(**exclude)

            library_ids = libraries.distinct().values_list("scpca_id", flat=True)

            if not library_ids:
                continue

            if sample_ids := (
                query["samples"]
                .filter(libraries__scpca_id__in=library_ids)
                .distinct()
                .values_list("scpca_id", flat=True)
            ):
                summaries.append(
                    {
                        "samples_count": len(sample_ids),
                        "name": query["name"],
                        "format": query.get("format", common.FORMAT_EXTENSIONS.get(self.format)),
                    }
                )

        return summaries

    def get_project_diagnoses(self) -> Dict:
        """
        Returns dict where key is a project id in the dataset and value is the number of
        samples (excluding bulk) with that diagnosis in the dataset for that project.
        """
        samples = self.get_selected_samples([Modalities.SINGLE_CELL, Modalities.SPATIAL])

        diagnoses_counts = {key: Counter() for key in self.data.keys()}

        for project_id, diagnosis in samples.values_list("project__scpca_id", "diagnosis"):
            diagnoses_counts[project_id].update({diagnosis: 1})

        return diagnoses_counts

    def get_project_modality_counts(self) -> Dict[str, Dict[Modalities, int]]:
        """
        Returns a dict where the key is a project id in the dataset and
        the value is an object of the following samples that are present
        in the dataset for that project:
        - SINGLE_CELL
        - SPATIAL
        - BULK_RNA_SEQ
        """
        counts: dict[str, dict] = defaultdict(dict)

        single_cell_count = dict(
            self.get_selected_samples([Modalities.SINGLE_CELL])
            .values("project__scpca_id")
            .annotate(num_samples=Count("project__scpca_id"))
            .order_by("project__scpca_id")
            .values_list("project__scpca_id", "num_samples")
        )

        spatial_count = dict(
            self.get_selected_samples([Modalities.SPATIAL])
            .values("project__scpca_id")
            .annotate(num_samples=Count("project__scpca_id"))
            .order_by("project__scpca_id")
            .values_list("project__scpca_id", "num_samples")
        )

        bulk_count = dict(
            self.get_selected_samples([Modalities.BULK_RNA_SEQ])
            .values("project__scpca_id")
            .annotate(num_samples=Count("project__scpca_id"))
            .order_by("project__scpca_id")
            .values_list("project__scpca_id", "num_samples")
        )

        for project_id in self.data.keys():
            counts[project_id][Modalities.SINGLE_CELL] = single_cell_count.get(project_id, 0)
            if Project.objects.filter(scpca_id=project_id, has_spatial_data=True).exists():
                counts[project_id][Modalities.SPATIAL] = spatial_count.get(project_id, 0)
            if bulk_sample_count := bulk_count.get(project_id, 0):
                counts[project_id][Modalities.BULK_RNA_SEQ] = bulk_sample_count

        return counts

    def get_project_titles(self) -> Dict:
        return {
            scpca_id: title for scpca_id, title in self.projects.values_list("scpca_id", "title")
        }

    def get_modality_count_mismatch_projects(self) -> List[str]:
        """
        Returns a list of project ids where the samples differ between the SINGLE_CELL
        and SPATIAL modalities (i.e., samples are present in one modality but not the other).
        """
        dataset_samples = self.get_selected_samples(
            [Modalities.SINGLE_CELL, Modalities.SPATIAL]
        ).values_list("scpca_id", "project__scpca_id", "has_single_cell_data", "has_spatial_data")

        project_modality_samples = defaultdict(lambda: defaultdict(set))
        for (
            scpca_id,
            project__scpca_id,
            has_single_cell_data,
            has_spatial_data,
        ) in dataset_samples:
            if has_single_cell_data:
                project_modality_samples[project__scpca_id][Modalities.SINGLE_CELL].add(scpca_id)
            if has_spatial_data:
                project_modality_samples[project__scpca_id][Modalities.SPATIAL].add(scpca_id)

        mismatch_project_ids = []
        for project_id, modalities in self.data.items():
            # Early exit if either modality has no samples
            if not modalities[Modalities.SINGLE_CELL] or not modalities[Modalities.SPATIAL]:
                continue

            single_cell_samples = project_modality_samples[project_id][Modalities.SINGLE_CELL]
            spatial_samples = project_modality_samples[project_id][Modalities.SPATIAL]

            if single_cell_samples ^ spatial_samples:
                mismatch_project_ids.append(project_id)

        return mismatch_project_ids

    def get_project_sample_counts(self) -> Dict[str, int]:
        """
        Returns a dict where the key is a project id in the dataset and
        the value is the total count of unique samples combined across
        SINGLE_CELL and SPATIAL modalities (excluding BULK_RNA_SEQ) for that project.
        """
        return dict(
            self.get_selected_samples([Modalities.SINGLE_CELL, Modalities.SPATIAL])
            .distinct()
            .values("project__scpca_id")
            .annotate(num_samples=Count("project__scpca_id"))
            .order_by("project__scpca_id")
            .values_list("project__scpca_id", "num_samples")
        )

    @property
    def download_filename(self) -> str:
        # User Datasets have a default DatasetFormat of SINGLE_CELL_EXERPIMENT,
        # though many of their files are of FileFormat SPATIAL_SPACERANGER.
        # The ouptut format depends on the format requested
        # for the rest of the data included in the dataset.
        output_format = "-".join(self.format.split("_")).lower()
        date = utils.get_today_string()

        return f"{self.id}_{output_format}_{date}.zip"

    @property
    def download_url(self) -> str | None:
        """A temporary URL from which the file can be downloaded."""
        if not self.computed_file:
            return None

        return self.computed_file.get_dataset_download_url(self.download_filename)
