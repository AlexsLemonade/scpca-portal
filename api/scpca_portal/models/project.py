import csv
import json
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Set

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.template.loader import render_to_string

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
        return self.input_data_path / f"{self.scpca_id}_bulk_metadata.tsv"

    @property
    def input_bulk_quant_file_path(self):
        return self.input_data_path / f"{self.scpca_id}_bulk_quant.tsv"

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

    def create_readmes(self) -> None:
        """
        Creates all possible readmes to be included later when archiving the desired computed file.
        """
        self.create_anndata_readme_file()
        self.create_anndata_merged_readme_file()
        self.create_metadata_readme_file()
        self.create_multiplexed_readme_file()
        self.create_single_cell_readme_file()
        self.create_single_cell_merged_readme_file()
        self.create_spatial_readme_file()

    def create_anndata_readme_file(self):
        """Creates an annotation metadata README file."""
        with open(ComputedFile.README_ANNDATA_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_ANNDATA_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_anndata_merged_readme_file(self):
        """Creates an annotation metadata README file."""
        with open(ComputedFile.README_ANNDATA_MERGED_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_ANNDATA_MERGED_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_single_cell_readme_file(self):
        """Creates a single cell metadata README file."""
        with open(ComputedFile.README_SINGLE_CELL_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_SINGLE_CELL_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_single_cell_merged_readme_file(self):
        """Creates a single cell metadata README file."""
        with open(ComputedFile.README_SINGLE_CELL_MERGED_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_SINGLE_CELL_MERGED_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_metadata_readme_file(self):
        """Creates a metadata only README file."""
        with open(ComputedFile.README_METADATA_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_METADATA_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        # This list of included projects will need to be built differently
                        # when the time comes to handle multiple projects at the same time
                        "included_projects": [(self.scpca_id, self.url)],
                    },
                ).strip()
            )

    def create_multiplexed_readme_file(self):
        """Creates a multiplexed metadata README file."""
        with open(ComputedFile.README_MULTIPLEXED_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_MULTIPLEXED_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_spatial_readme_file(self):
        """Creates a spatial metadata README file."""
        with open(ComputedFile.README_SPATIAL_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_SPATIAL_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

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
                computed_file.process_computed_file(clean_up_output_data, update_s3)
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

    @classmethod
    def get_from_dict(cls, data: Dict):
        project = cls(
            scpca_id=data.pop("scpca_project_id"),
        )

        # Assign values to remaining properties
        for key in data.keys():
            if hasattr(project, key):
                if key.startswith("includes_") or key.startswith("has_"):
                    setattr(project, key, utils.boolean_from_string(data.get(key, False)))
                else:
                    setattr(project, key, data.get(key))

        project.data_file_paths = project.get_data_file_paths()

        return project

    def get_data_file_paths(self) -> List[Path]:
        """
        Retrieves existing merged and bulk data file paths on the aws input bucket
        and returns them as a list.
        """
        merged_relative_path = Path(f"{self.scpca_id}/merged/")
        bulk_relative_path = Path(f"{self.scpca_id}/{self.scpca_id}_bulk")

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

    def get_demux_sample_ids(self) -> Set:
        """Returns a set of all demuxed sample ids used in the project's multiplexed samples."""
        demux_sample_ids = set()
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            multiplexed_sample_dir_demux_ids = multiplexed_sample_dir.name.split(",")
            demux_sample_ids.update(multiplexed_sample_dir_demux_ids)

        return demux_sample_ids

    def get_multiplexed_aggregate_fields(self):
        """
        Retrieves the project's aggregate values of demux cell counter, seq units, and technologies,
        (found within the library json files), and returns the three as a dictionary.
        """
        multiplexed_sample_demux_cell_counter = Counter()
        multiplexed_sample_seq_units_mapping = {}
        multiplexed_sample_technologies_mapping = {}
        for filename_path in sorted(Path(self.input_data_path).rglob("*,*/*_metadata.json")):
            with open(filename_path) as multiplexed_json_file:
                multiplexed_json = json.load(multiplexed_json_file)

            multiplexed_sample_demux_cell_counter.update(multiplexed_json["sample_cell_estimates"])

            # Gather seq_units and technologies data.
            for demux_sample_id in multiplexed_json["demux_samples"]:
                # This if check is necessary because it's possible for one sample
                # to be multiplexed multiple times in the same project
                if demux_sample_id not in multiplexed_sample_seq_units_mapping:
                    multiplexed_sample_seq_units_mapping[demux_sample_id] = set()
                if demux_sample_id not in multiplexed_sample_technologies_mapping:
                    multiplexed_sample_technologies_mapping[demux_sample_id] = set()

                multiplexed_sample_seq_units_mapping[demux_sample_id].add(
                    multiplexed_json["seq_unit"].strip()
                )
                multiplexed_sample_technologies_mapping[demux_sample_id].add(
                    multiplexed_json["technology"].strip()
                )

        return {
            "sample_demux_cell_counter": multiplexed_sample_demux_cell_counter,
            "sample_seq_units_mapping": multiplexed_sample_seq_units_mapping,
            "sample_technologies_mapping": multiplexed_sample_technologies_mapping,
        }

    def get_multiplexed_with_mapping(self) -> Dict[str, Set]:
        """
        Return a dictionary with keys being specific demux ids,
        and the values being all ids that this sample was multiplexed with.
        """
        multiplexed_with_mapping = {}
        for multiplexed_dir in sorted(Path(self.input_data_path).rglob("*,*/")):
            multiplexed_ids = set(multiplexed_dir.name.split(","))
            for id in multiplexed_ids:
                multiplexed_with_mapping[id] = multiplexed_ids.difference({id})

        return multiplexed_with_mapping

    def get_multiplexed_with_combined_metadata(
        self,
        scpca_sample_id,
        multiplexed_with_mapping,
        multiplexed_combined_metadata_by_sample,
    ):
        """
        Returns a list of combined_metadata of all samples
        that the given sample was multiplexed with.
        """

        multiplexed_with_combined_metadata = []
        current_sample_library_ids = set(
            library["scpca_library_id"]
            for library in multiplexed_combined_metadata_by_sample[scpca_sample_id]
        )
        multiplexed_sample_ids = sorted(multiplexed_with_mapping[scpca_sample_id])

        for multiplexed_sample_id in multiplexed_sample_ids:
            multiplexed_with_combined_metadata.extend(
                [
                    library
                    for library in multiplexed_combined_metadata_by_sample[multiplexed_sample_id]
                    # In general, the multiplexed_sample_id was multiplexed with the current sample,
                    # but we have to clarify that the right libraries are accounted for.
                    if library["scpca_library_id"] in current_sample_library_ids
                ]
            )

        return multiplexed_with_combined_metadata

    def get_multiplexed_library_path_mapping(self) -> Dict:
        """Returns dictionary which maps library ids to their location in the filesystem."""
        multiplexed_library_path_mapping = {}
        # Sort and iterate over multiplexed directories
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            # Sort and iterate over libraries within those directories
            for filename_path in sorted(Path(multiplexed_sample_dir).rglob("*_metadata.json")):
                library_id = filename_path.name.split("_")[0]
                multiplexed_library_path_mapping[library_id] = multiplexed_sample_dir

        return multiplexed_library_path_mapping

    def get_non_downloadable_sample_ids(self) -> Set:
        """
        Retrieves set of all ids which are not currently downloadable.
        Some samples will exist but their contents cannot be shared yet.
        When this happens their corresponding sample folder will not exist.
        """
        with open(self.input_samples_metadata_file_path) as samples_csv_file:
            samples_metadata = [sample for sample in csv.DictReader(samples_csv_file)]

        non_downloadable_sample_ids = set()

        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            sample_dir = self.get_sample_input_data_dir(scpca_sample_id)
            if not sample_dir.exists():
                non_downloadable_sample_ids.add(scpca_sample_id)

        return non_downloadable_sample_ids

    def get_library_metadata_keys(self, all_keys, modalities=()):
        """Returns a set of library metadata keys based on the modalities context."""
        excluded_keys = {
            "scpca_sample_id",
        }

        if Sample.Modalities.CITE_SEQ not in modalities:
            excluded_keys.add("has_citeseq")

        if Sample.Modalities.SPATIAL in modalities:
            excluded_keys.update(
                (
                    "filtered_cells",
                    "filtered_spots",
                    "tissue_spots",
                    "unfiltered_cells",
                    "unfiltered_spots",
                )
            )

        return all_keys.difference(excluded_keys)

    def get_combined_metadata_by_sample(
        self, all_samples_combined_metadata_by_modality: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Iterates over a list of unsorted library metadata dicts
        and organizes them into a dictionary with keys being sample ids
        and values being a list of the sample's associated libraries.
        """
        combined_metadata_by_sample = {}
        for library in all_samples_combined_metadata_by_modality:
            if library["scpca_sample_id"] not in combined_metadata_by_sample:
                combined_metadata_by_sample[library["scpca_sample_id"]] = []
            combined_metadata_by_sample[library["scpca_sample_id"]].append(library)

        return combined_metadata_by_sample

    def get_sample_libraries_mapping(self, libraries_metadata):
        """
        Returns a dictionary which maps sample ids to a set of associated library ids.
        """
        sample_libraries_id_mapping = {}

        for library_metadata in libraries_metadata:
            is_not_multiplexed = "demux_samples" not in library_metadata

            if is_not_multiplexed:
                if library_metadata["scpca_sample_id"] not in sample_libraries_id_mapping:
                    sample_libraries_id_mapping[library_metadata["scpca_sample_id"]] = set()

                sample_libraries_id_mapping[library_metadata["scpca_sample_id"]].add(
                    library_metadata["scpca_library_id"]
                )
            else:
                multiplexed_library_sample_ids = library_metadata["demux_samples"]
                for multiplexed_sample_id in multiplexed_library_sample_ids:
                    if multiplexed_sample_id not in sample_libraries_id_mapping:
                        sample_libraries_id_mapping[multiplexed_sample_id] = set()
                    sample_libraries_id_mapping[multiplexed_sample_id].add(
                        library_metadata["scpca_library_id"]
                    )

        return sample_libraries_id_mapping

    def get_sample_metadata_keys(self, all_keys, modalities=()):
        """Returns a set of metadata keys based on the modalities context."""
        excluded_keys = {
            "demux_cell_count_estimate",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
            "multiplexed_with",
            "seq_units",
            "technologies",
        }

        if Sample.Modalities.MULTIPLEXED in modalities:
            excluded_keys.update(
                (
                    "alevin_fry_version",
                    "date_processed",
                    "filtered_cell_count",
                    "mapped_reads",
                    "scpca_library_id",
                    "sample_cell_count_estimate",
                    "total_reads",
                    "workflow",
                    "workflow_commit",
                    "workflow_version",
                )
            )

        if Sample.Modalities.SPATIAL in modalities:
            excluded_keys.update(
                (
                    "alevin_fry_version",
                    "filtered_cell_count",
                    "filtering_method",
                    "salmon_version",
                    "sample_cell_count_estimate",
                    "transcript_type",
                    "unfiltered_cells",
                    "workflow_version",
                )
            )

        return all_keys.difference(excluded_keys)

    def get_multiplexed_samples_metadata(
        self, updated_samples_metadata: List[Dict], sample_id: str
    ) -> List:
        """Returns a list of samples metadata after filtering out all nonmultiplexed samples."""
        multiplexed_sample_ids = self.get_demux_sample_ids()  # Unified multiplexed sample ID set.

        multiplexed_samples_metadata = []

        for sample_metadata in updated_samples_metadata:
            multiplexed_sample_id = sample_metadata["scpca_sample_id"]
            if multiplexed_sample_id not in multiplexed_sample_ids:  # Skip non-multiplexed samples.
                continue

            if sample_id and multiplexed_sample_id != sample_id:
                continue

            multiplexed_samples_metadata.append(sample_metadata)

        return multiplexed_samples_metadata

    def get_sample_input_data_dir(self, sample_scpca_id):
        """Returns an input data directory based on a sample ID."""
        return self.input_data_path / sample_scpca_id

    def load_data(self, sample_id: str = None, **kwargs) -> None:
        """
        Goes through a project directory's contents, parses multiple level metadata
        files, writes combined metadata into resulting files.

        Returns a list of project's computed files.
        """
        self.create_readmes()

        # Parses tsv sample metadata file, massages field names
        samples_metadata = self.load_samples_metadata()

        # Parses json library metadata files, massages field names, calculates aggregate values
        self.load_libraries_metadata(samples_metadata)

        # Updates sample properties that are derived from recently saved libraries
        self.update_sample_derived_properties()

        # Updates project properties that are derived from recently saved samples
        self.update_project_derived_properties()

        Sample.create_computed_files(
            self, kwargs["max_workers"], kwargs["clean_up_output_data"], kwargs["update_s3"]
        )

        self.create_computed_files(
            kwargs["max_workers"], kwargs["clean_up_output_data"], kwargs["update_s3"]
        )

    def load_samples_metadata(self) -> List[Dict]:
        samples_metadata = metadata_file.load_samples_metadata(
            self.input_samples_metadata_file_path
        )

        Sample.bulk_create_from_dicts(samples_metadata, self)

        return samples_metadata

    def load_libraries_metadata(self, samples_metadata: List[Dict]):
        library_metadata_paths = set(Path(self.input_data_path).rglob("*_metadata.json"))
        all_libraries_metadata = [
            metadata_file.load_library_metadata(lib_path) for lib_path in library_metadata_paths
        ]
        for library_metadata in all_libraries_metadata:
            # Multiplexed samples are represented in scpca_sample_id as comma separated lists
            # This ensures that all samples with be related to the correct library
            for sample_id in library_metadata["scpca_sample_id"].split(","):
                sample = self.samples.get(scpca_id=sample_id)
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
        # Set modality flags based on a real data availability.
        bulk_rna_seq_sample_ids = self.get_bulk_rna_seq_sample_ids()

        for sample in self.samples.all():
            sample.has_bulk_rna_seq = sample.scpca_id in bulk_rna_seq_sample_ids
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

    def get_download_config_file_paths(self, download_config: Dict) -> List[Path]:
        """
        Return all of a project's file paths that are suitable for the passed download config.
        """
        if download_config["includes_merged"]:
            omit_suffixes = set(common.FORMAT_EXTENSIONS.values())
            omit_suffixes.remove(common.FORMAT_EXTENSIONS.get(download_config["format"], None))

            return [
                file_path
                for file_path in [Path(fp) for fp in self.data_file_paths]
                if file_path.suffix not in omit_suffixes
            ]

        return [
            file_path
            for file_path in [Path(fp) for fp in self.data_file_paths]
            if file_path.parent.name != "merged"
        ]
