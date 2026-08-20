from typing import TYPE_CHECKING, Dict, List, Self, Set

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Func, QuerySet

from scpca_portal import metadata_parser, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.models.base import CommonDataAttributes
from scpca_portal.models.library import Library
from scpca_portal.models.loadable_resource_abc import LoadableResourceABC
from scpca_portal.models.original_file import OriginalFile

if TYPE_CHECKING:
    from scpca_portal.models import Project

logger = get_and_configure_logger(__name__)


class Sample(CommonDataAttributes, LoadableResourceABC):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    age = models.TextField()
    age_timing = models.TextField()
    demux_cell_count_estimate_sum = models.IntegerField(null=True)
    diagnosis = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_multiplexed_data = models.BooleanField(default=False)
    has_single_cell_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    includes_anndata = models.BooleanField(default=False)
    is_cell_line = models.BooleanField(default=False)
    is_xenograft = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    multiplexed_with = ArrayField(models.TextField(), default=list)
    sample_cell_count_estimate = models.IntegerField(null=True)
    scpca_id = models.TextField(unique=True)
    seq_units = ArrayField(models.TextField(), default=list)
    sex = models.TextField(blank=True, null=True)
    subdiagnosis = models.TextField(blank=True, null=True)
    technologies = ArrayField(models.TextField(), default=list)
    tissue_location = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="samples")
    libraries = models.ManyToManyField(Library, related_name="samples")

    SCPCA_RESOURCE_METADATA_ID_KEY = "scpca_sample_id"
    SCPCA_RESOURCE_ORIGINAL_FILE_ID_KEY = "sample_id"

    def __str__(self) -> str:
        return f"Sample {self.scpca_id} of {self.project}"

    # TODO: remove before loadable resource feature branch lands
    @classmethod
    def get_from_dict(cls, data: Dict, project: "Project") -> Self:
        """Prepares ready for saving sample object."""
        sample = cls(
            age=data["age"],
            age_timing=data["age_timing"],
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            is_cell_line=utils.boolean_from_string(data.get("is_cell_line", False)),
            is_xenograft=utils.boolean_from_string(data.get("is_xenograft", False)),
            metadata=data,
            multiplexed_with=data.get("multiplexed_with", []),
            sample_cell_count_estimate=(data.get("sample_cell_count_estimate", None)),
            project=project,
            scpca_id=data["scpca_sample_id"],
            seq_units=data.get("seq_units", []),
            sex=data["sex"],
            subdiagnosis=data["subdiagnosis"],
            technologies=data.get("technologies", []),
            tissue_location=data["tissue_location"],
            treatment=data.get("treatment", ""),
        )

        return sample

    def update_from_dict(self, data: Dict) -> Self:
        """Prepares ready for saving sample object."""
        self.age = (data["age"],)
        self.age_timing = (data["age_timing"],)
        self.diagnosis = (data["diagnosis"],)
        self.disease_timing = (data["disease_timing"],)
        self.is_cell_line = (utils.boolean_from_string(data.get("is_cell_line", False)),)
        self.is_xenograft = (utils.boolean_from_string(data.get("is_xenograft", False)),)
        self.metadata = (data,)
        self.multiplexed_with = (data.get("multiplexed_with", []),)
        self.sample_cell_count_estimate = ((data.get("sample_cell_count_estimate", None)),)
        self.seq_units = (data.get("seq_units", []),)
        self.sex = (data["sex"],)
        self.subdiagnosis = (data["subdiagnosis"],)
        self.technologies = (data.get("technologies", []),)
        self.tissue_location = (data["tissue_location"],)
        self.treatment = (data.get("treatment", ""),)

        return self

    @classmethod
    def bulk_create_from_dicts(cls, samples_metadata: List[Dict], project: "Project") -> None:
        """Creates a list of sample objects from sample metadata libraries and then saves them."""
        samples = []
        for sample_metadata in samples_metadata:
            samples.append(Sample.get_from_dict(sample_metadata, project))

        Sample.objects.bulk_create(samples)

    @classmethod
    def get_all_input_metadata_files(
        cls, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> QuerySet[OriginalFile]:
        return OriginalFile.objects.filter(
            is_metadata=True,
            # this comes to exclude bulk metadata files,
            # though bulk samples exist in the samples metadata files
            is_bulk=False,
            project_id__isnull=False,
            sample_ids=[],
            library_id__isnull=True,
            s3_bucket=bucket,
        )

    @classmethod
    def load_all_metadata(
        cls, metadata_files: QuerySet[OriginalFile], *, filter_on_ids: Set[str] | None = None
    ) -> List[Dict]:
        return metadata_parser.load_all_samples_metadata(
            metadata_files, filter_on_ids=filter_on_ids
        )

    # TODO: remove before loadable resource feature branch lands
    @classmethod
    def load_metadata(cls, project: "Project") -> None:
        """
        Parses sample metadata csv, creates Sample objects,
        loads library metadata for the given project, and
        updates sample aggregate values.
        """
        samples_metadata = metadata_parser.load_samples_metadata(project.scpca_id)

        Sample.bulk_create_from_dicts(samples_metadata, project)

        Library.load_metadata(project)

        # Update sample properties based on library queries after processing all samples
        Sample.update_modality_properties(project)
        Sample.update_aggregate_properties(project)

    @classmethod
    def update_aggregate_properties(cls, project: "Project") -> None:
        """
        The Sample model caches aggregated library metadata.
        We need to update these after libraries are added/deleted.
        """
        updated_samples = []
        updated_attrs = [
            "seq_units",
            "technologies",
            "multiplexed_with",
            "demux_cell_count_estimate_sum",
            "sample_cell_count_estimate",
        ]

        for sample in project.samples.all():
            libraries = sample.libraries.all()

            # Sequencing Units
            seq_units = {
                seq_unit
                for library in libraries
                if (seq_unit := library.metadata.get("seq_unit", "").strip())
            }
            sample.seq_units = sorted(seq_units, key=str.lower)

            # Technologies
            technologies = {
                technology
                for library in libraries
                if (technology := library.metadata.get("technology", "").strip())
            }
            sample.technologies = sorted(technologies, key=str.lower)

            if multiplexed_libraries := sample.libraries.filter(is_multiplexed=True):
                # Cache all sample ID's related through the multiplexed libraries.
                sample.multiplexed_with = list(
                    sample.multiplexed_with_samples.order_by("scpca_id").values_list(
                        "scpca_id", flat=True
                    )
                )
                # Sum of all related libraries' sample_cell_estimates for that sample.
                sample.demux_cell_count_estimate_sum = sum(
                    library.metadata["sample_cell_estimates"].get(sample.scpca_id, 0)
                    for library in multiplexed_libraries
                )
            else:
                # Sum of filtered_cell_count from non-multiplexed Single-cell libraries.
                sample.sample_cell_count_estimate = sum(
                    library.metadata.get("filtered_cell_count", 0)
                    for library in libraries.filter(
                        modality=Modalities.SINGLE_CELL, is_multiplexed=False
                    )
                )
            updated_samples.append(sample)

        Sample.objects.bulk_update(updated_samples, updated_attrs)

    @classmethod
    def update_modality_properties(cls, project: "Project") -> None:
        """
        Updates sample modality properties,
        derived from the existence of a certain attribute within a collection of Libraries.
        """
        updated_samples = []
        updated_attrs = [
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
            "includes_anndata",
        ]
        # Set modality flags based on a real data availability.
        for sample in project.samples.all():
            sample.has_bulk_rna_seq = sample.scpca_id in project.get_bulk_rna_seq_sample_ids()
            sample.has_cite_seq_data = sample.libraries.filter(has_cite_seq_data=True).exists()
            sample.has_multiplexed_data = sample.libraries.filter(is_multiplexed=True).exists()
            sample.has_single_cell_data = sample.libraries.filter(
                modality=Modalities.SINGLE_CELL
            ).exists()
            sample.has_spatial_data = sample.libraries.filter(modality=Modalities.SPATIAL).exists()
            sample.includes_anndata = sample.libraries.filter(
                formats__contains=[FileFormats.ANN_DATA]
            ).exists()
            updated_samples.append(sample)

        Sample.objects.bulk_update(updated_samples, updated_attrs)

    @classmethod
    def create_new_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> None:
        existing_sample_ids = set(cls.objects.values_list("scpca_id", flat=True))
        new_original_file_sample_project_id_pairs = set(
            OriginalFile.objects.exclude(sample_ids=[])
            .annotate(sample_id=Func(F("sample_ids"), function="unnest"))
            .exclude(sample_id__in=existing_sample_ids)
            .values_list("sample_id", "project_id")
            .distinct()
        )
        new_metadata_sample_project_id_pairs = set(
            (sample_id, project_id)
            for project_id, sample_id, _ in cls.get_metadata_id_tuples(
                metadata_dicts_by_ids.values()
            )
            if sample_id not in existing_sample_ids
        )
        new_sample_project_id_pairs = (
            new_original_file_sample_project_id_pairs | new_metadata_sample_project_id_pairs
        )

        if not new_sample_project_id_pairs:
            return

        # Resolve Project via the FK's related_model
        # to avoid a circular import (Project already imports Sample)
        Project = cls._meta.get_field("project").related_model
        projects_by_id = Project.objects.in_bulk(
            [project_id for _, project_id in new_sample_project_id_pairs], field_name="scpca_id"
        )

        new_samples = [
            cls(scpca_id=new_sample_id, project=projects_by_id[project_id])
            for new_sample_id, project_id in new_sample_project_id_pairs
        ]
        cls.objects.bulk_create(new_samples)

    @classmethod
    def remove_deleted_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> None:
        # TODO: before merging into dev: do we need to clarify mechanism to alert user datasets?
        existing_sample_ids = set(
            OriginalFile.objects.exclude(sample_ids=[])
            .annotate(sample_id=Func(F("sample_ids"), function="unnest"))
            .values_list("sample_id", flat=True)
        ) | set(metadata_dicts_by_ids.keys())

        cls.objects.exclude(scpca_id__in=existing_sample_ids).delete()

    @classmethod
    def get_original_file_filter_on_kwargs(cls, filter_on_ids: List) -> Dict:
        return {f"{cls.SCPCA_RESOURCE_ORIGINAL_FILE_ID_KEY}__overlap": filter_on_ids}

    @staticmethod
    def get_lockfile_filter_kwargs(lockfile_project_ids: List) -> Dict:
        return {"project__scpca_id__in": lockfile_project_ids}

    @property
    def additional_metadata(self) -> dict[str, str]:
        return {
            key: value
            for key, value in self.metadata.items()
            if not hasattr(self, key)
            # These fields are accounted for elsewhere,
            # either in different models or by different names
            and key not in ("scpca_sample_id", "scpca_project_id", "submitter")
        }

    @property
    def loaded_original_files(self) -> QuerySet[OriginalFile]:
        """
        This property returns all files, from sample down to library, associated with the sample,
        whether downloadable or not.
        """
        return OriginalFile.objects.filter(sample_ids__contains=[self.scpca_id])

    def get_metadata(self) -> Dict:
        excluded_metadata_attributes = {
            "scpca_project_id",
            "submitter",  # included in project metadata under the name pi_name
        }

        sample_metadata = {
            key: value
            for key, value in self.metadata.items()
            if key not in excluded_metadata_attributes
        }
        sample_metadata["includes_anndata"] = self.includes_anndata

        return sample_metadata

    @property
    def modalities(self) -> list[Modalities]:
        attr_name_modality_mapping = {
            "has_bulk_rna_seq": Modalities.BULK_RNA_SEQ,
            "has_cite_seq_data": Modalities.CITE_SEQ,
            "has_multiplexed_data": Modalities.MULTIPLEXED,
            "has_single_cell_data": Modalities.SINGLE_CELL,
            "has_spatial_data": Modalities.SPATIAL,
        }

        return utils.get_sorted_modalities(
            [
                modality_name
                for attr_name, modality_name in attr_name_modality_mapping.items()
                if getattr(self, attr_name)
            ]
        )

    @property
    def multiplexed_with_samples(self) -> QuerySet[Self]:
        return (
            Sample.objects.filter(libraries__in=self.libraries.filter(is_multiplexed=True))
            .distinct()
            .exclude(scpca_id=self.scpca_id)
        )

    @property
    def multiplexed_ids(self) -> List[str]:
        multiplexed_sample_ids = [self.scpca_id]
        multiplexed_sample_ids.extend(self.multiplexed_with)

        return sorted(multiplexed_sample_ids)

    @property
    def is_last_multiplexed_sample(self) -> bool:
        """Return True if sample id is highest in list of multiplexed ids, False if not"""
        return self.scpca_id == self.multiplexed_ids[-1]

    def purge(self) -> None:
        """Purges a sample and its associated libraries"""
        for library in self.libraries.all():
            # If library has other samples that it is related to, then don't delete it
            if library.samples.count() == 1:
                library.delete()
        self.delete()

    def purge_computed_files(self, delete_from_s3: bool = False) -> None:
        for computed_file in self.sample_computed_files.all():
            computed_file.purge(delete_from_s3)
