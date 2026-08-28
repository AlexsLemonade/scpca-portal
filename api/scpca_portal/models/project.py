import csv
from collections import Counter
from typing import Dict, List, Set

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, Q, QuerySet

from typing_extensions import Self

from scpca_portal import common, metadata_parser, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import Modalities
from scpca_portal.models.aggregatable_resource_abc import AggregatableResourceABC
from scpca_portal.models.base import CommonDataAttributes
from scpca_portal.models.contact import Contact
from scpca_portal.models.external_accession import ExternalAccession
from scpca_portal.models.library import Library
from scpca_portal.models.loadable_resource_abc import LoadableResourceABC
from scpca_portal.models.original_file import OriginalFile
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.publication import Publication
from scpca_portal.models.sample import Sample

logger = get_and_configure_logger(__name__)


class Project(CommonDataAttributes, LoadableResourceABC, AggregatableResourceABC):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    abstract = models.TextField()
    additional_metadata_keys = ArrayField(models.TextField(), default=list)
    additional_restrictions = models.TextField(blank=True, null=True)
    diagnoses = ArrayField(models.TextField(), default=list)
    diagnoses_counts = models.JSONField(default=dict)
    disease_timings = ArrayField(models.TextField(), default=list)
    downloadable_sample_count = models.IntegerField(default=0)
    has_single_cell_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    human_readable_pi_name = models.TextField()
    includes_anndata = models.BooleanField(default=False)
    includes_cell_lines = models.BooleanField(default=False)
    includes_merged_anndata = models.BooleanField(default=False)
    includes_merged_sce = models.BooleanField(default=False)
    includes_xenografts = models.BooleanField(default=False)
    # TODO: remove attr when feature branch is merged in
    is_locked = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    modalities = ArrayField(models.TextField(), default=list)
    multiplexed_sample_count = models.IntegerField(default=0)
    organisms = ArrayField(models.TextField(), default=list)
    pi_name = models.TextField()
    s3_input_bucket = models.TextField(default=settings.AWS_S3_INPUT_BUCKET_NAME)
    sample_count = models.IntegerField(default=0)
    scpca_id = models.TextField(unique=True)
    seq_units = ArrayField(models.TextField(), default=list)
    technologies = ArrayField(models.TextField(), default=list)
    title = models.TextField()
    unavailable_samples_count = models.PositiveIntegerField(default=0)

    contacts = models.ManyToManyField(Contact)
    external_accessions = models.ManyToManyField(ExternalAccession)
    publications = models.ManyToManyField(Publication)

    SCPCA_RESOURCE_METADATA_ID_KEY = "scpca_project_id"
    SCPCA_RESOURCE_ORIGINAL_FILE_ID_KEY = "project_id"

    def __str__(self) -> str:
        return f"Project {self.scpca_id}"

    # TODO: refactor to match update_from_dict before loadable resource feature branch lands
    @classmethod
    def get_from_dict(cls, data: Dict) -> Self:
        project = cls(scpca_id=data.pop("scpca_project_id"))
        # Assign values to remaining properties
        for key in data.keys():
            if hasattr(project, key):
                if key.startswith("includes_") or key.startswith("has_"):
                    setattr(project, key, utils.boolean_from_string(data.get(key, False)))
                else:
                    setattr(project, key, data.get(key))
        project.metadata = data

        return project

    def update_from_dict(self, data: Dict) -> Self:
        for key, value in data.items():
            if not hasattr(self, key) or key == "scpca_portal_id":
                continue

            if key.startswith("includes_") or key.startswith("has_"):
                value = utils.boolean_from_string(data.get(key, False))

            setattr(self, key, value)
        self.metadata = data

        return self

    @classmethod
    def lock_projects(cls, locked_project_ids: List[str]) -> List[Self]:
        locked_projects = []
        for project in cls.objects.filter(scpca_id__in=locked_project_ids):
            project.is_locked = True
            locked_projects.append(project)
        cls.objects.bulk_update(locked_projects, ["is_locked"])

        return locked_projects

    @property
    def modality_samples(self) -> Dict[str, List[str]]:
        """Return a dictionary of lists containing sample IDs, grouped by modality."""
        return {
            Modalities.SINGLE_CELL: list(
                self.samples.filter(has_single_cell_data=True).values_list("scpca_id", flat=True)
            ),
            Modalities.SPATIAL: list(
                self.samples.filter(has_spatial_data=True).values_list("scpca_id", flat=True)
            ),
        }

    @property
    def multiplexed_samples(self) -> List[str]:
        """Return a lists containing multiplexed sample IDs."""
        if not self.has_multiplexed_data:
            return []
        return list(
            self.samples.filter(has_multiplexed_data=True).values_list("scpca_id", flat=True)
        )

    @property
    def original_files(self) -> QuerySet[OriginalFile]:
        """
        This property returns all downloadable project level files associated with the project.
        """
        return OriginalFile.downloadable_objects.filter(
            project_id=self.scpca_id, is_project_file=True
        )

    @property
    def original_file_paths(self) -> List[str]:
        return sorted(self.original_files.values_list("s3_key", flat=True))

    @property
    def loaded_original_files(self) -> QuerySet[OriginalFile]:
        """
        This property returns all files, from project down to library, associated with the project,
        whether downloadable or not.
        """
        return OriginalFile.objects.filter(project_id=self.scpca_id)

    @property
    def url(self) -> str:
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"

    def get_metadata(self) -> Dict:
        return {
            "scpca_project_id": self.scpca_id,
            "pi_name": self.pi_name,
            "project_title": self.title,
        }

    def get_downloadable_sample_count(self) -> int:
        """
        Returns the count of unique samples with the corresponding input files on S3.
        """
        sample_ids_queryset = OriginalFile.downloadable_objects.filter(
            project_id=self.scpca_id, sample_ids__isnull=False
        ).values_list("sample_ids", flat=True)

        return len(set().union(*sample_ids_queryset))

    def get_bulk_rna_seq_sample_ids(self) -> Set[str]:
        """Returns set of bulk RNA sequencing sample IDs."""
        bulk_rna_seq_sample_ids = set()
        if self.has_bulk_rna_seq:
            bulk_metadata_file = OriginalFile.get_input_project_bulk_metadata_file(self.scpca_id)
            with open(bulk_metadata_file.local_file_path, "r") as bulk_metadata_file:
                bulk_rna_seq_sample_ids.update(
                    (
                        line["sample_id"]
                        for line in csv.DictReader(bulk_metadata_file, delimiter=common.TAB)
                    )
                )
        return bulk_rna_seq_sample_ids

    @classmethod
    def get_all_input_metadata_files(
        cls, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> QuerySet[OriginalFile]:
        return OriginalFile.objects.filter(is_metadata=True, project_id=None, s3_bucket=bucket)

    @classmethod
    def load_all_metadata(
        cls, metadata_files: QuerySet[OriginalFile], *, filter_on_ids: Set[str] | None = None
    ) -> List[Dict]:
        projects_metadata_file = metadata_files.first()
        return metadata_parser.load_all_projects_metadata(
            projects_metadata_file, filter_on_ids=filter_on_ids
        )

    # TODO: remove before loadable resource feature branch lands
    def load_metadata(self) -> None:
        """
        Loads sample metadata and updates project aggregate values.
        """
        Sample.load_metadata(self)

        # Update project properties based on sample queries after processing all samples
        self.update_project_modality_properties()
        self.update_project_aggregate_properties()
        self.update_project_sample_aggregate_counts()
        self.update_project_summaries_aggregate_properties()

    @property
    def current_aggregation_hash(self) -> str:
        samples_metadata_hashes = self.samples.sort_by("scpca_id").values_list(
            "metadata_hash", flat=True
        )
        libraries_metadata_hashes = self.libraries.sort_by("scpca_id").values_list(
            "metadata_hash", flat=True
        )
        return utils.hash_values(samples_metadata_hashes + libraries_metadata_hashes)

    def update_aggregations(self) -> None:
        self.new_update_project_modality_properties()
        self.new_update_project_aggregate_properties()
        self.new_update_project_sample_aggregate_counts()
        self.new_update_project_summaries_aggregate_properties()

    @classmethod
    def create_new_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> List[Self]:
        existing_project_ids = cls.objects.values_list("scpca_id", flat=True)
        new_project_ids = set(metadata_dicts_by_ids.keys()) - set(existing_project_ids)

        if not new_project_ids:
            return []

        new_projects = [cls(scpca_id=new_project_id) for new_project_id in new_project_ids]
        return cls.objects.bulk_create(new_projects)

    @classmethod
    def remove_deleted_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> tuple[int, dict]:
        existing_project_ids = set(
            OriginalFile.objects.exclude(project_id__isnull=True).values_list(
                "project_id", flat=True
            )
        ) | set(metadata_dicts_by_ids.keys())

        return cls.objects.exclude(scpca_id__in=existing_project_ids).delete()

    @staticmethod
    def get_lockfile_filter_kwargs(lockfile_project_ids: List) -> Dict:
        return {"project__scpca_id__in": lockfile_project_ids}

    def purge(self, delete_from_s3: bool = False) -> None:
        """Purges project and its related data."""
        self.purge_computed_files(delete_from_s3)
        for sample in self.samples.all():
            sample.purge()

        self.delete()

    # TODO: remove before loadable resource feature branch lands
    def purge_computed_files(self, delete_from_s3: bool = False) -> None:
        """Purges all computed files associated with the project instance."""
        # Delete project's sample computed files
        for sample in self.samples.all():
            sample.purge_computed_files(delete_from_s3)

        # Delete project's project computed files
        for computed_file in self.project_computed_files.all():
            computed_file.purge(delete_from_s3)

    # TODO: remove before loadable resource feature branch lands
    def update_project_modality_properties(self) -> None:
        """
        Updates project modality properties,
        which are derived from the existence of a certain attribute within a collection of Samples.
        """

        # Set modality flags based on a real data availability.
        self.has_bulk_rna_seq = self.samples.filter(has_bulk_rna_seq=True).exists()
        self.has_cite_seq_data = self.samples.filter(has_cite_seq_data=True).exists()
        self.has_multiplexed_data = self.samples.filter(has_multiplexed_data=True).exists()
        self.has_single_cell_data = self.samples.filter(has_single_cell_data=True).exists()
        self.has_spatial_data = self.samples.filter(has_spatial_data=True).exists()
        self.includes_anndata = self.samples.filter(includes_anndata=True).exists()
        self.includes_cell_lines = self.samples.filter(is_cell_line=True).exists()
        self.includes_xenografts = self.samples.filter(is_xenograft=True).exists()
        self.save(
            update_fields=(
                "has_bulk_rna_seq",
                "has_cite_seq_data",
                "has_multiplexed_data",
                "has_single_cell_data",
                "has_spatial_data",
                "includes_anndata",
                "includes_cell_lines",
                "includes_xenografts",
            )
        )

    # TODO: drop new prefix from method when loadable feature branch is merged in
    def new_update_project_modality_properties(self) -> None:
        """
        Updates project modality properties,
        which are derived from the existence of a certain attribute within a collection of Samples.
        """

        # Set modality flags based on a real data availability.
        self.has_bulk_rna_seq = self.samples.filter(has_bulk_rna_seq=True).exists()
        self.has_cite_seq_data = self.samples.filter(has_cite_seq_data=True).exists()
        self.has_multiplexed_data = self.samples.filter(has_multiplexed_data=True).exists()
        self.has_single_cell_data = self.samples.filter(has_single_cell_data=True).exists()
        self.has_spatial_data = self.samples.filter(has_spatial_data=True).exists()
        self.includes_anndata = self.samples.filter(includes_anndata=True).exists()
        self.includes_cell_lines = self.samples.filter(is_cell_line=True).exists()
        self.includes_xenografts = self.samples.filter(is_xenograft=True).exists()

    # TODO: remove before loadable resource feature branch lands
    def update_project_aggregate_properties(self) -> None:
        """
        The Project model cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """
        samples = self.samples.all()

        # Additional Metadata Keys
        additional_metadata_keys = {
            key
            for sample in samples
            for key in sample.additional_metadata.keys()
            # Include keys except multiplexed_with
            if not (self.has_multiplexed_data and key == "multiplexed_with")
        }
        self.additional_metadata_keys = sorted(additional_metadata_keys, key=str.lower)

        # Diagnoses Counts
        self.diagnoses_counts = dict(Counter(samples.values_list("diagnosis", flat=True)))

        # Disease Timings excluding "NA"
        self.disease_timings = list(
            set(samples.values_list("disease_timing", flat=True)) - {common.NA}
        )

        # Modalities
        self.modalities = utils.get_sorted_modalities(
            {modality for sample in samples for modality in sample.modalities}
        )

        # Organisms
        organisms = {
            sample.additional_metadata["organism"]
            for sample in samples
            if "organism" in sample.additional_metadata
        }
        self.organisms = sorted(organisms)

        bulk_libraries = Library.objects.filter(samples__in=samples).exclude(
            modality=Modalities.BULK_RNA_SEQ
        )

        # Sequencing Units
        seq_units = {
            seq_unit
            for library in bulk_libraries
            if (seq_unit := library.metadata.get("seq_unit", "").strip())
        }
        self.seq_units = sorted(seq_units)

        # Technologies
        technologies = {
            technology
            for library in bulk_libraries
            if (technology := library.metadata.get("technology", "").strip())
        }
        self.technologies = sorted(technologies)

        self.save()

    # TODO: drop new prefix from method when loadable feature branch is merged in
    def new_update_project_aggregate_properties(self) -> None:
        """
        The Project model cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """
        samples = self.samples.all()

        # Additional Metadata Keys
        additional_metadata_keys = {
            key
            for sample in samples
            for key in sample.additional_metadata.keys()
            # Include keys except multiplexed_with
            if not (self.has_multiplexed_data and key == "multiplexed_with")
        }
        self.additional_metadata_keys = sorted(additional_metadata_keys, key=str.lower)

        # Diagnoses Counts
        self.diagnoses_counts = dict(Counter(samples.values_list("diagnosis", flat=True)))

        # Disease Timings excluding "NA"
        self.disease_timings = list(
            set(samples.values_list("disease_timing", flat=True)) - {common.NA}
        )

        # Modalities
        self.modalities = utils.get_sorted_modalities(
            {modality for sample in samples for modality in sample.modalities}
        )

        # Organisms
        organisms = {
            sample.additional_metadata["organism"]
            for sample in samples
            if "organism" in sample.additional_metadata
        }
        self.organisms = sorted(organisms)

        bulk_libraries = Library.objects.filter(samples__in=samples).exclude(
            modality=Modalities.BULK_RNA_SEQ
        )

        # Sequencing Units
        seq_units = {
            seq_unit
            for library in bulk_libraries
            if (seq_unit := library.metadata.get("seq_unit", "").strip())
        }
        self.seq_units = sorted(seq_units)

        # Technologies
        technologies = {
            technology
            for library in bulk_libraries
            if (technology := library.metadata.get("technology", "").strip())
        }
        self.technologies = sorted(technologies)

    # TODO: remove before loadable resource feature branch lands
    def update_project_sample_aggregate_counts(self) -> None:
        """
        The Project model cache aggregated sample counts.
        We need to update these after any project's sample gets added/deleted.
        """
        counts = self.samples.aggregate(
            sample_count=Count("scpca_id"),
            multiplexed_sample_count=Count("scpca_id", filter=Q(has_multiplexed_data=True)),
            unavailable_samples_count=Count(
                "scpca_id", filter=Q(has_single_cell_data=False, has_spatial_data=False)
            ),
        )
        self.downloadable_sample_count = self.get_downloadable_sample_count()
        self.sample_count = counts["sample_count"]
        self.multiplexed_sample_count = counts["multiplexed_sample_count"]
        self.unavailable_samples_count = counts["unavailable_samples_count"]

        self.save()

    # TODO: drop new prefix from method when loadable feature branch is merged in
    def new_update_project_sample_aggregate_counts(self) -> None:
        """
        The Project model cache aggregated sample counts.
        We need to update these after any project's sample gets added/deleted.
        """
        counts = self.samples.aggregate(
            sample_count=Count("scpca_id"),
            multiplexed_sample_count=Count("scpca_id", filter=Q(has_multiplexed_data=True)),
            unavailable_samples_count=Count(
                "scpca_id", filter=Q(has_single_cell_data=False, has_spatial_data=False)
            ),
        )
        self.downloadable_sample_count = self.get_downloadable_sample_count()
        self.sample_count = counts["sample_count"]
        self.multiplexed_sample_count = counts["multiplexed_sample_count"]
        self.unavailable_samples_count = counts["unavailable_samples_count"]

    # TODO: remove before loadable resource feature branch lands
    def update_project_summaries_aggregate_properties(self) -> None:
        """
        The ProjectSummary model cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """
        summaries_counts = Counter()

        for sample in self.samples.all():
            # We currently exclude bulk data in the project summary and aggregate values
            for library in sample.libraries.exclude(modality=Modalities.BULK_RNA_SEQ):
                seq_unit = library.metadata.get("seq_unit", "").strip()
                technology = library.metadata.get("technology", "").strip()
                summaries_counts.update({(sample.diagnosis, seq_unit, technology): 1})

        for (diagnosis, seq_unit, technology), count in summaries_counts.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=self, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count

            project_summary.save(update_fields=("sample_count",))

    # TODO: drop new prefix from method when loadable feature branch is merged in
    def new_update_project_summaries_aggregate_properties(self) -> None:
        """
        The ProjectSummary model cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """
        summaries_counts = Counter()

        for sample in self.samples.all():
            # We currently exclude bulk data in the project summary and aggregate values
            for library in sample.libraries.exclude(modality=Modalities.BULK_RNA_SEQ):
                seq_unit = library.metadata.get("seq_unit", "").strip()
                technology = library.metadata.get("technology", "").strip()
                summaries_counts.update({(sample.diagnosis, seq_unit, technology): 1})

        project_summaries = []
        for (diagnosis, seq_unit, technology), count in summaries_counts.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=self, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count
            project_summaries.append(project_summary)

        ProjectSummary.objects.bulk_update(project_summaries, fields=["sample_count"])
