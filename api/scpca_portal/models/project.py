import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, Q

from scpca_portal import common, metadata_parser, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.contact import Contact
from scpca_portal.models.external_accession import ExternalAccession
from scpca_portal.models.library import Library
from scpca_portal.models.original_file import OriginalFile
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.publication import Publication
from scpca_portal.models.sample import Sample

logger = get_and_configure_logger(__name__)


class Project(CommonDataAttributes, TimestampedModel):
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

    def __str__(self):
        return f"Project {self.scpca_id}"

    @classmethod
    def get_from_dict(cls, data: Dict):
        project = cls(scpca_id=data.pop("scpca_project_id"))
        # Assign values to remaining properties
        for key in data.keys():
            if hasattr(project, key):
                if key.startswith("includes_") or key.startswith("has_"):
                    setattr(project, key, utils.boolean_from_string(data.get(key, False)))
                else:
                    setattr(project, key, data.get(key))

        return project

    @property
    def samples_to_generate(self):
        """Return all non multiplexed samples and only one sample from multiplexed libraries."""
        return [sample for sample in self.samples.all() if sample.is_last_multiplexed_sample]

    @property
    def valid_download_config_names(self) -> List[str]:
        return [
            download_config_name
            for download_config_name, download_config in common.PROJECT_DOWNLOAD_CONFIGS.items()
            if self.get_libraries(download_config).exists()
        ]

    @property
    def valid_download_configs(self) -> List[Dict]:
        return [
            download_config
            for download_config in common.PROJECT_DOWNLOAD_CONFIGS.values()
            if self.get_libraries(download_config).exists()
        ]

    @property
    def original_files(self):
        return OriginalFile.downloadable_objects.filter(
            project_id=self.scpca_id, is_project_file=True
        )

    @property
    def original_file_paths(self) -> List[str]:
        return sorted(self.original_files.values_list("s3_key", flat=True))

    @property
    def computed_files(self) -> Iterable[ComputedFile]:
        return self.project_computed_files.order_by("created_at")

    @property
    def input_data_path(self):
        return settings.INPUT_DATA_PATH / self.scpca_id

    @property
    def input_merged_data_path(self):
        return self.input_data_path / "merged"

    @property
    def input_bulk_metadata_file_path(self):
        return self.input_data_path / "bulk" / f"{self.scpca_id}_bulk_metadata.tsv"

    @property
    def input_bulk_quant_file_path(self):
        return self.input_data_path / "bulk" / f"{self.scpca_id}_bulk_quant.tsv"

    @property
    def input_merged_summary_report_file_path(self):
        return self.input_merged_data_path / f"{self.scpca_id}_merged-summary-report.html"

    @property
    def input_samples_metadata_file_path(self):
        return self.input_data_path / "samples_metadata.csv"

    @property
    def url(self):
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"

    def get_metadata(self) -> Dict:
        return {
            "scpca_project_id": self.scpca_id,
            "pi_name": self.pi_name,
            "project_title": self.title,
        }

    def get_libraries(self, download_config: Dict = {}):  # -> QuerySet[Library]:
        """
        Return all of a project's associated libraries filtered by the passed download config.
        """
        if not download_config or download_config.get("metadata_only"):
            return self.libraries.all()

        if download_config not in common.PROJECT_DOWNLOAD_CONFIGS.values():
            raise ValueError("Invalid download_config passed. Unable to retrieve libraries.")

        # You cannot include multiplexed when there are no multiplexed libraries
        if not download_config["excludes_multiplexed"] and not self.has_multiplexed_data:
            return self.libraries.none()

        if download_config["includes_merged"]:
            # If the download config requests merged and there is no merged file in the project,
            # return an empty queryset
            if (
                download_config["format"] == FileFormats.SINGLE_CELL_EXPERIMENT
                and not self.includes_merged_sce
            ):
                return self.libraries.none()
            elif (
                download_config["format"] == FileFormats.ANN_DATA
                and not self.includes_merged_anndata
            ):
                return self.libraries.none()

        # non-bulk libraries
        libraries_queryset = self.libraries.filter(
            modality=download_config["modality"],
            formats__contains=[download_config["format"]],
        )

        if download_config["excludes_multiplexed"]:
            return libraries_queryset.exclude(is_multiplexed=True)

        return libraries_queryset

    def get_output_file_name(self, download_config: Dict) -> str:
        """
        Accumulates all applicable name segments, concatenates them with an underscore delimiter,
        and returns the string as a unique zip file name.
        """
        if download_config.get("metadata_only", False):
            return f"{self.scpca_id}_ALL_METADATA.zip"

        name_segments = [self.scpca_id, download_config["modality"], download_config["format"]]
        if download_config.get("includes_merged", False):
            name_segments.append("MERGED")

        if not download_config.get("excludes_multiplexed", False) and self.has_multiplexed_data:
            name_segments.append("MULTIPLEXED")

        # Change to filename format must be accompanied by an entry in the docs.
        # Each segment should have hyphens and no underscores
        # Each segment should be joined by underscores
        file_name = "_".join([segment.replace("_", "-") for segment in name_segments])

        return f"{file_name}.zip"

    def get_computed_file(self, download_config: Dict) -> ComputedFile:
        "Return the project computed file that matches the passed download_config."
        if download_config["metadata_only"]:
            return self.computed_files.filter(metadata_only=True).first()

        return self.computed_files.filter(
            modality=download_config["modality"],
            format=download_config["format"],
            has_multiplexed_data=(not download_config["excludes_multiplexed"]),
            includes_merged=download_config["includes_merged"],
        ).first()

    def get_bulk_rna_seq_sample_ids(self):
        """Returns set of bulk RNA sequencing sample IDs."""
        bulk_rna_seq_sample_ids = set()
        if self.has_bulk_rna_seq:
            with open(self.input_bulk_metadata_file_path, "r") as bulk_metadata_file:
                bulk_rna_seq_sample_ids.update(
                    (
                        line["sample_id"]
                        for line in csv.DictReader(bulk_metadata_file, delimiter=common.TAB)
                    )
                )
        return bulk_rna_seq_sample_ids

    def get_original_files_by_download_config(self, download_config: Dict):
        """
        Return all of a project's file paths that are suitable for the passed download config.
        """
        # Spatial samples do not have bulk or merged project files
        if download_config["modality"] == Modalities.SPATIAL:
            return OriginalFile.objects.none()

        original_files = OriginalFile.downloadable_objects.filter(
            project_id=self.scpca_id, is_project_file=True
        )

        if download_config["includes_merged"]:
            if download_config["format"] == FileFormats.ANN_DATA:
                return original_files.exclude(is_single_cell_experiment=True)
            if download_config["format"] == FileFormats.SINGLE_CELL_EXPERIMENT:
                return original_files.exclude(is_anndata=True)

        return original_files.filter(is_merged=False)

    def load_metadata(self) -> None:
        """
        Loads sample and library metadata files, creates Sample and Library objects,
        and archives Project and Sample computed files.
        """
        self.load_samples()
        self.load_libraries()
        if self.has_bulk_rna_seq:
            self.load_bulk_libraries()

        self.update_sample_derived_properties()
        self.update_project_derived_properties()

    def load_samples(self) -> None:
        """
        Parses sample metadata csv and creates Sample objects
        """
        samples_metadata = metadata_parser.load_samples_metadata(
            self.input_samples_metadata_file_path
        )

        Sample.bulk_create_from_dicts(samples_metadata, self)

    def load_libraries(self) -> None:
        """
        Parses library metadata json files and creates Library objects
        """
        library_metadata_paths = set(Path(self.input_data_path).rglob("*_metadata.json"))
        all_libraries_metadata = [
            metadata_parser.load_library_metadata(lib_path) for lib_path in library_metadata_paths
        ]
        for library_metadata in all_libraries_metadata:
            # Multiplexed samples are represented in scpca_sample_id as comma separated lists
            # This ensures that all samples with be related to the correct library
            for sample_id in library_metadata["scpca_sample_id"].split(","):
                # We create samples based on what is in samples_metadata.csv
                # If the sample folder is in the input bucket, but not listed
                # we should skip creating that library as the sample won't exist.
                if sample := self.samples.filter(scpca_id=sample_id).first():
                    Library.bulk_create_from_dicts([library_metadata], sample)

    def load_bulk_libraries(self) -> None:
        """
        Parses bulk metadata tsv files and create Library objets for bulk-only samples
        """
        if not self.has_bulk_rna_seq:
            raise Exception("Trying to load bulk libraries for project with no bulk data")

        all_bulk_libraries_metadata = metadata_parser.load_bulk_metadata(
            self.input_bulk_metadata_file_path
        )
        for library_metadata in all_bulk_libraries_metadata:
            sample_id = library_metadata["scpca_sample_id"]
            if sample := self.samples.filter(scpca_id=sample_id).first():
                Library.bulk_create_from_dicts([library_metadata], sample)

    def purge(self, delete_from_s3: bool = False) -> None:
        """Purges project and its related data."""
        self.purge_computed_files(delete_from_s3)
        for sample in self.samples.all():
            sample.purge()

        self.delete()

    def purge_computed_files(self, delete_from_s3: bool = False) -> None:
        """Purges all computed files associated with the project instance."""
        # Delete project's sample computed files
        for sample in self.samples.all():
            sample.purge_computed_files(delete_from_s3)

        # Delete project's project computed files
        for computed_file in self.project_computed_files.all():
            computed_file.purge(delete_from_s3)

    def update_sample_derived_properties(self):
        """
        Updates sample properties that are derived from the querying of library data
        after all samples have been processed.
        """
        self.update_sample_modality_properties()
        self.update_sample_aggregate_properties()

    def update_sample_modality_properties(self):
        """
        Updates sample modality properties,
        derived from the existence of a certain attribute within a collection of Libraries.
        """
        # Set modality flags based on a real data availability.
        for sample in self.samples.all():
            sample.has_bulk_rna_seq = sample.scpca_id in self.get_bulk_rna_seq_sample_ids()
            sample.has_cite_seq_data = sample.libraries.filter(has_cite_seq_data=True).exists()
            sample.has_multiplexed_data = sample.libraries.filter(is_multiplexed=True).exists()
            sample.has_single_cell_data = sample.libraries.filter(
                modality=Modalities.SINGLE_CELL
            ).exists()
            sample.has_spatial_data = sample.libraries.filter(modality=Modalities.SPATIAL).exists()
            sample.includes_anndata = sample.libraries.filter(
                formats__contains=[FileFormats.ANN_DATA]
            ).exists()
            sample.save(
                update_fields=(
                    "has_bulk_rna_seq",
                    "has_cite_seq_data",
                    "has_multiplexed_data",
                    "has_single_cell_data",
                    "has_spatial_data",
                    "includes_anndata",
                )
            )

    def update_sample_aggregate_properties(self):
        """
        The Sample model caches aggregated library metadata.
        We need to update these after libraries are added/deleted.
        """
        for sample in self.samples.all():
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

            sample.save()

    def update_project_derived_properties(self):
        """
        Updates project properties that are derived from the querying of Sample data
        after all Samples have been processed.
        """
        self.update_project_modality_properties()
        self.update_project_aggregate_properties()
        self.update_project_sample_aggregate_counts()
        self.update_project_summaries_aggregate_properties()

    def update_project_modality_properties(self):
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

    def update_project_aggregate_properties(self):
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

    def update_project_sample_aggregate_counts(self):
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
        self.sample_count = counts["sample_count"]
        self.multiplexed_sample_count = counts["multiplexed_sample_count"]
        self.unavailable_samples_count = counts["unavailable_samples_count"]

        self.save()

    def update_project_summaries_aggregate_properties(self):
        """
        The ProjectSummary model cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """
        summaries_counts = Counter()

        for sample in self.samples.all():
            # We currently exlude bulk data in the project summary and aggregate values
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

    def update_downloadable_sample_count(self):
        """
        Retrieves downloadable sample counts after the uploading of computed files to s3,
        updates the corresponding attributes on the project object, and saves the object to the db.
        """
        self.downloadable_sample_count = (
            self.samples.filter(sample_computed_files__isnull=False).distinct().count()
        )
        self.save()
