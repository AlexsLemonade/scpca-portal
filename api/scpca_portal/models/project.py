import csv
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models

from scpca_portal import common, metadata_file, utils
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.contact import Contact
from scpca_portal.models.external_accession import ExternalAccession
from scpca_portal.models.library import Library
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.publication import Publication
from scpca_portal.models.sample import Sample

logger = logging.getLogger()


class Project(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    abstract = models.TextField()
    additional_metadata_keys = models.TextField(blank=True, null=True)
    additional_restrictions = models.TextField(blank=True, null=True)
    data_file_paths = ArrayField(models.TextField(), default=list)
    diagnoses = models.TextField(blank=True, null=True)
    diagnoses_counts = models.TextField(blank=True, null=True)
    disease_timings = models.TextField()
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
    sample_count = models.IntegerField(default=0)
    scpca_id = models.TextField(unique=True)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
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

        project.data_file_paths = project.get_data_file_paths()

        return project

    @staticmethod
    def get_input_project_metadata_file_path():
        return common.INPUT_DATA_PATH / "project_metadata.csv"

    @property
    def computed_files(self):
        return self.project_computed_files.order_by("created_at")

    @property
    def input_data_path(self):
        return common.INPUT_DATA_PATH / self.scpca_id

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
    def multiplexed_computed_file(self):
        try:
            return self.project_computed_files.get(
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                has_multiplexed_data=True,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                includes_merged=False,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_merged_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                includes_merged=True,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                includes_merged=False,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_merged_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                includes_merged=True,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def spatial_computed_file(self):
        try:
            return self.project_computed_files.get(
                modality=ComputedFile.OutputFileModalities.SPATIAL
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def url(self):
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"

    def get_metadata(self) -> Dict:
        return {
            "scpca_project_id": self.scpca_id,
            "pi_name": self.pi_name,
            "project_title": self.title,
        }

    def get_download_config_file_output_name(self, download_config: Dict) -> str:
        """
        Accumulates all applicable name segments, concatenates them with an underscore delimiter,
        and returns the string as a unique zip file name.
        """
        if download_config.get("metadata_only", False):
            return f"{self.scpca_id}_ALL_METADATA.zip"

        name_segments = [self.scpca_id, download_config["modality"], download_config["format"]]
        if download_config.get("includes_merged", False):
            name_segments.append("MERGED")

        if self.has_multiplexed_data and not download_config.get("excludes_multiplexed", False):
            name_segments.append("MULTIPLEXED")

        return f"{'_'.join(name_segments)}.zip"

    def create_computed_files(
        self,
        max_workers=8,  # 8 = 2 file formats * 4 mappings.
        clean_up_output_data=True,
        update_s3=False,
    ):
        """Prepares ready for saving project computed files based on generated file mappings."""

        def on_get_project_file(future):
            if computed_file := future.result():
                computed_file.save()

                if update_s3:
                    computed_file.upload_s3_file()
                if clean_up_output_data:
                    computed_file.clean_up_local_computed_file()

            # Close DB connection for each thread.
            connection.close()

        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for download_config in common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS:
                tasks.submit(
                    ComputedFile.get_project_file,
                    self,
                    download_config,
                    self.get_download_config_file_output_name(download_config),
                ).add_done_callback(on_get_project_file)

        self.update_downloadable_sample_count()

    def get_data_file_paths(self) -> List[Path]:
        """
        Retrieves existing merged and bulk data file paths on the aws input bucket
        and returns them as a list.
        """
        merged_relative_path = Path(f"{self.scpca_id}/merged/")
        bulk_relative_path = Path(f"{self.scpca_id}/bulk/")

        data_file_paths = utils.list_s3_paths(merged_relative_path) + utils.list_s3_paths(
            bulk_relative_path
        )

        return data_file_paths

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

    def get_additional_terms(self):
        if not self.additional_restrictions:
            return ""

        with open(
            common.TEMPLATE_PATH / "readme/additional_terms/research_academic_only.md"
        ) as additional_terms_file:
            return additional_terms_file.read()

    def get_download_config_file_paths(self, download_config: Dict) -> List[Path]:
        """
        Return all of a project's file paths that are suitable for the passed download config.
        """
        # Spatial samples do not have bulk or merged project files
        if download_config["modality"] == Library.Modalities.SPATIAL:
            return []

        data_file_path_objects = [Path(fp) for fp in self.data_file_paths]

        if download_config["includes_merged"]:
            omit_suffixes = set(common.FORMAT_EXTENSIONS.values())
            omit_suffixes.remove(common.FORMAT_EXTENSIONS.get(download_config["format"], None))

            return [
                file_path
                for file_path in data_file_path_objects
                if file_path.suffix not in omit_suffixes
            ]

        return [
            file_path for file_path in data_file_path_objects if file_path.parent.name != "merged"
        ]

    def load_data(self, **kwargs) -> None:
        """
        Loads sample and library metadata files, creates Sample and Library objects,
        and archives Project and Sample computed files.
        """
        self.load_samples()
        self.load_libraries()

        self.update_sample_derived_properties()
        self.update_project_derived_properties()

        Sample.create_computed_files(
            self, kwargs["max_workers"], kwargs["clean_up_output_data"], kwargs["update_s3"]
        )

        self.create_computed_files(
            kwargs["max_workers"], kwargs["clean_up_output_data"], kwargs["update_s3"]
        )

    def load_samples(self) -> List[Dict]:
        """
        Parses sample metadata csv and creates Sample objects
        """
        samples_metadata = metadata_file.load_samples_metadata(
            self.input_samples_metadata_file_path
        )

        Sample.bulk_create_from_dicts(samples_metadata, self)

    def load_libraries(self):
        """
        Parses library metadata json files and creates Library objects
        """
        library_metadata_paths = set(Path(self.input_data_path).rglob("*_metadata.json"))
        all_libraries_metadata = [
            metadata_file.load_library_metadata(lib_path) for lib_path in library_metadata_paths
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

    def purge(self, delete_from_s3=False):
        """Purges project and its related data."""
        for sample in self.samples.all():
            for computed_file in sample.computed_files:
                if delete_from_s3:
                    computed_file.delete_s3_file(force=True)
                computed_file.delete()
            for library in sample.libraries.all():
                # If library has other samples that it is related to, then don't delete it
                if len(library.samples.all()) == 1:
                    library.delete()
            sample.delete()

        for computed_file in self.computed_files:
            if delete_from_s3:
                computed_file.delete_s3_file(force=True)
            computed_file.delete()

        ProjectSummary.objects.filter(project=self).delete()
        self.delete()

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
                modality=Library.Modalities.SINGLE_CELL
            ).exists()
            sample.has_spatial_data = sample.libraries.filter(
                modality=Library.Modalities.SPATIAL
            ).exists()
            sample.includes_anndata = sample.libraries.filter(
                formats__contains=[Library.FileFormats.ANN_DATA]
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
            sample_cell_count_estimate = 0
            sample_seq_units = set()
            sample_technologies = set()

            for library in sample.libraries.all():
                if library.modality == Library.Modalities.SINGLE_CELL:
                    if not library.is_multiplexed:
                        sample_cell_count_estimate += library.metadata.get("filtered_cell_count")

                sample_seq_units.add(library.metadata["seq_unit"].strip())
                sample_technologies.add(library.metadata["technology"].strip())

            sample.seq_units = ", ".join(sorted(sample_seq_units, key=str.lower))
            sample.technologies = ", ".join(sorted(sample_technologies, key=str.lower))

            if multiplexed_library := sample.libraries.filter(is_multiplexed=True).first():
                multiplexed_ids = set(s.scpca_id for s in multiplexed_library.samples.all())
                sample.multiplexed_with = sorted(multiplexed_ids.difference({sample.scpca_id}))
                sample.demux_cell_count_estimate = multiplexed_library.metadata[
                    "sample_cell_estimates"
                ].get(sample.scpca_id)
            else:
                sample.sample_cell_count_estimate = sample_cell_count_estimate

            sample.save()

    def update_project_derived_properties(self):
        """
        Updates project properties that are derived from the querying of Sample data
        after all Samples have been processed.
        """
        self.update_project_modality_properties()
        self.update_project_aggregate_properties()

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
        The Project and ProjectSummary models cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """

        additional_metadata_keys = set()
        diagnoses = set()
        diagnoses_counts = Counter()
        disease_timings = set()
        modalities = set()
        organisms = set()
        seq_units = set()
        summaries_counts = Counter()
        technologies = set()

        for sample in self.samples.all():
            additional_metadata_keys.update(sample.additional_metadata.keys())
            diagnoses.add(sample.diagnosis)
            diagnoses_counts.update({sample.diagnosis: 1})
            disease_timings.add(sample.disease_timing)
            modalities.update(sample.modalities)
            if "organism" in sample.additional_metadata:
                organisms.add(sample.additional_metadata["organism"])

            sample_seq_units = sample.seq_units.split(", ")
            sample_technologies = sample.technologies.split(", ")
            for seq_unit in sample_seq_units:
                for technology in sample_technologies:
                    summaries_counts.update(
                        {(sample.diagnosis, seq_unit.strip(), technology.strip()): 1}
                    )

            seq_units.update(sample_seq_units)
            technologies.update(sample_technologies)

        diagnoses_strings = sorted(
            (f"{diagnosis} ({count})" for diagnosis, count in diagnoses_counts.items())
        )
        multiplexed_sample_count = self.samples.filter(has_multiplexed_data=True).count()
        sample_count = self.samples.count()
        seq_units = sorted((seq_unit for seq_unit in seq_units if seq_unit))
        technologies = sorted((technology for technology in technologies if technology))

        if self.has_multiplexed_data and "multiplexed_with" in additional_metadata_keys:
            additional_metadata_keys.remove("multiplexed_with")

        self.additional_metadata_keys = ", ".join(sorted(additional_metadata_keys, key=str.lower))
        self.diagnoses = ", ".join(sorted(diagnoses))
        self.diagnoses_counts = ", ".join(diagnoses_strings)
        self.disease_timings = ", ".join(disease_timings)
        self.modalities = sorted(modalities)
        self.multiplexed_sample_count = multiplexed_sample_count
        self.organisms = sorted(organisms)
        self.sample_count = sample_count
        self.seq_units = ", ".join(seq_units)
        self.technologies = ", ".join(technologies)
        self.save()

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
        downloadable_sample_count = (
            self.samples.filter(sample_computed_files__isnull=False).distinct().count()
        )
        sample_count = self.samples.count()
        non_downloadable_samples_count = self.samples.filter(
            has_multiplexed_data=False, has_single_cell_data=False, has_spatial_data=False
        ).count()
        unavailable_samples_count = max(
            sample_count - downloadable_sample_count - non_downloadable_samples_count, 0
        )

        self.downloadable_sample_count = downloadable_sample_count
        self.unavailable_samples_count = unavailable_samples_count
        self.save()
