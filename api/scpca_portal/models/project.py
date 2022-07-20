import csv
import json
import logging
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List

from django.db import models

from scpca_portal import common
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.sample import Sample

logger = logging.getLogger()


class Project(TimestampedModel):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    abstract = models.TextField(null=False)
    additional_metadata_keys = models.TextField(blank=True, null=True)
    contact_email = models.TextField(null=True)
    contact_name = models.TextField(null=True)
    diagnoses = models.TextField(blank=True, null=True)
    diagnoses_counts = models.TextField(blank=True, null=True)
    disease_timings = models.TextField(null=False)
    downloadable_sample_count = models.IntegerField(default=0)
    has_bulk_rna_seq = models.BooleanField(default=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_multiplexed_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    human_readable_pi_name = models.TextField(null=False)
    modalities = models.TextField(blank=True, null=True)
    multiplexed_sample_count = models.IntegerField(default=0)
    pi_name = models.TextField(null=False)
    sample_count = models.IntegerField(default=0)
    scpca_id = models.TextField(unique=True, null=False)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    title = models.TextField(null=False)

    def __str__(self):
        return f"Project {self.scpca_id}"

    @staticmethod
    def get_input_project_metadata_file_path():
        return os.path.join(common.INPUT_DATA_DIR, "project_metadata.csv")

    @property
    def computed_files(self):
        return self.project_computed_files.order_by("created_at")

    @property
    def input_data_dir(self):
        return os.path.join(common.INPUT_DATA_DIR, self.scpca_id)

    @property
    def input_bulk_metadata_file_path(self):
        return os.path.join(self.input_data_dir, f"{self.scpca_id}_bulk_metadata.tsv")

    @property
    def input_bulk_quant_file_path(self):
        return os.path.join(self.input_data_dir, f"{self.scpca_id}_bulk_quant.tsv")

    @property
    def input_samples_metadata_file_path(self):
        return os.path.join(self.input_data_dir, "samples_metadata.csv")

    @property
    def multiplexed_computed_file(self):
        try:
            return self.project_computed_files.get(
                type=ComputedFile.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def output_multiplexed_computed_file_name(self):
        return f"{self.scpca_id}_multiplexed.zip"

    @property
    def output_multiplexed_metadata_field_order(self):
        return [
            "scpca_sample_id",
            "scpca_library_id",
            "scpca_project_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "spaceranger_version",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age",
            "sex",
            "tissue_location",
            "treatment",
            "participant_id",
            "submitter",
            "submitter_id",
        ]

    @property
    def output_multiplexed_metadata_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{self.scpca_id}_multiplexed_metadata.tsv")

    @property
    def output_multiplexed_metadata_ignored_fields(self):
        return {
            "injected": (
                "demux_cell_count_estimate",
                "has_cite_seq_data",
                "has_spatial_data",
                "sample_cell_count_estimate",
                "seq_units",
                "technologies",
            ),
            "library": ("scpca_sample_id",),
            "single_cell": (
                "alevin_fry_version",
                "date_processed",
                "filtered_cell_count",
                "mapped_reads",
                "scpca_library_id",
                "seq_units",
                "technologies",
                "total_reads",
                "workflow",
                "workflow_commit",
                "workflow_version",
            ),
        }

    @property
    def output_single_cell_metadata_field_order(self):
        return [
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "seq_unit",
            "technology",
            "sample_cell_count_estimate",
            "scpca_project_id",
            "pi_name",
            "project_title",
            "disease_timing",
            "age",
            "sex",
            "tissue_location",
        ]

    @property
    def output_single_cell_metadata_ignored_fields(self):
        return [
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_spatial_data",
            "seq_units",
            "technologies",
        ]

    @property
    def output_single_cell_computed_file_name(self):
        return f"{self.scpca_id}.zip"

    @property
    def output_single_cell_metadata_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{self.scpca_id}_libraries_metadata.tsv")

    @property
    def output_spatial_computed_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_metadata_field_order(self):
        return [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "spaceranger_version",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age",
            "sex",
            "tissue_location",
            "treatment",
            "participant_id",
            "submitter",
            "submitter_id",
        ]

    @property
    def output_spatial_metadata_ignored_fields(self):
        return {
            "injected": (
                "has_bulk_rna_seq",
                "has_cite_seq_data",
                "has_spatial_data",
                "sample_cell_count_estimate",
                "seq_units",
                "technologies",
            ),
            "library": (
                "filtered_cells",
                "filtered_spots",
                "tissue_spots",
                "unfiltered_cells",
                "unfiltered_spots",
            ),
            "single_cell": (
                "alevin_fry_version",
                "filtered_cell_count",
                "filtering_method",
                "has_citeseq",
                "salmon_version",
                "seq_units",
                "technologies",
                "transcript_type",
                "unfiltered_cells",
                "workflow_version",
            ),
        }

    @property
    def output_spatial_metadata_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{self.scpca_id}_spatial_metadata.tsv")

    @property
    def single_cell_computed_file(self):
        try:
            return self.project_computed_files.get(type=ComputedFile.OutputFileTypes.PROJECT_ZIP)
        except ComputedFile.DoesNotExist:
            pass

    @property
    def spatial_computed_file(self):
        try:
            return self.project_computed_files.get(
                type=ComputedFile.OutputFileTypes.PROJECT_SPATIAL_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def url(self):
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"

    def combine_multiplexed_metadata(
        self,
        samples_metadata: List[Dict],
        multiplexed_libraries_metadata: List[Dict],
        scpca_sample_ids: List[str],
    ):
        """Combines the two metadata dicts together to have all multiplexed data
        at the library level. Writes the combination out to the project and
        sample metadata files. The sample file also includes multiplexed samples.
        """

        combined_metadata = list()
        multiplexed_sample_mapping = dict()
        if not multiplexed_libraries_metadata:
            return combined_metadata, multiplexed_sample_mapping

        # Get all the field names to pass to the csv.DictWriter
        all_fields = set(multiplexed_libraries_metadata[0].keys())
        all_fields.update(
            set(samples_metadata[0].keys())
            - set(self.output_multiplexed_metadata_ignored_fields["injected"])
            - set(self.output_multiplexed_metadata_ignored_fields["single_cell"])
        )

        ordered_fields = self.output_multiplexed_metadata_field_order
        all_fields -= set(ordered_fields)
        ordered_fields.extend(sorted(all_fields, key=str.lower))  # The resulting field order.

        multiplexed_library_mapping = dict()  # Sample ID to library IDs mapping.
        multiplexed_sample_ids = set()  # Unified multiplexed sample ID set.
        for library in multiplexed_libraries_metadata:
            multiplexed_library_sample_ids = library["demux_samples"]
            for multiplexed_sample_id in multiplexed_library_sample_ids:
                # Populate multiplexed library mapping.
                if multiplexed_sample_id not in multiplexed_library_mapping:
                    multiplexed_library_mapping[multiplexed_sample_id] = set()
                multiplexed_library_mapping[multiplexed_sample_id].add(library["scpca_library_id"])

                # Add sample IDs to a unified set.
                multiplexed_sample_ids.update(multiplexed_library_sample_ids)

                # Remove sample ID from a mapping as sample cannot be
                # multiplexed with itself.
                multiplexed_library_sample_ids_copy = set(multiplexed_library_sample_ids)
                multiplexed_library_sample_ids_copy.discard(multiplexed_sample_id)

                # Populate multiplexed sample mapping.
                if multiplexed_sample_id not in multiplexed_sample_mapping:
                    multiplexed_sample_mapping[multiplexed_sample_id] = set()
                multiplexed_sample_mapping[multiplexed_sample_id].update(
                    multiplexed_library_sample_ids_copy
                )

        # Generate multiplexed sample metadata dict.
        sample_metadata_mapping = dict()
        for sample_metadata in samples_metadata:
            multiplexed_sample_id = sample_metadata["scpca_sample_id"]
            if multiplexed_sample_id not in multiplexed_sample_ids:  # Skip non-multiplexed samples.
                continue

            if scpca_sample_ids and multiplexed_sample_id not in scpca_sample_ids:
                continue

            sample_metadata_copy = sample_metadata.copy()
            # Exclude fields.
            field_names = (
                self.output_multiplexed_metadata_ignored_fields["injected"]
                + self.output_multiplexed_metadata_ignored_fields["single_cell"]
            )
            for field_name in field_names:
                if field_name not in sample_metadata_copy:
                    continue
                sample_metadata_copy.pop(field_name)

            sample_metadata_copy["pi_name"] = self.pi_name
            sample_metadata_copy["project_title"] = self.title
            sample_metadata_copy["scpca_project_id"] = self.scpca_id

            sample_metadata_mapping[multiplexed_sample_id] = sample_metadata_copy

        # Combine and write the metadata.
        combined_metadata_added_pair_ids = set()
        for sample_id in sorted(sample_metadata_mapping.keys()):
            sample_metadata_path = Sample.get_output_multiplexed_metadata_file_path(sample_id)
            with open(sample_metadata_path, "w", newline="") as sample_file:
                sample_csv_writer = csv.DictWriter(
                    sample_file, fieldnames=ordered_fields, delimiter=common.TAB
                )
                sample_csv_writer.writeheader()

                multiplexed_sample_ids = sorted(multiplexed_sample_mapping[sample_id])
                multiplexed_sample_ids.insert(0, sample_id)  # Current sample libraries go first.
                for multiplexed_sample_id in multiplexed_sample_ids:
                    libraries = sorted(
                        (
                            library
                            for library in multiplexed_libraries_metadata
                            if library["scpca_library_id"] in multiplexed_library_mapping[sample_id]
                        ),
                        key=lambda l: l["scpca_library_id"],
                    )
                    for library in libraries:
                        # Exclude fields.
                        for field_name in self.output_multiplexed_metadata_ignored_fields[
                            "library"
                        ]:
                            if field_name not in library:
                                continue
                            library.pop(field_name)

                        library_copy = library.copy()
                        library_copy.update(sample_metadata_mapping.get(multiplexed_sample_id, {}))
                        sample_csv_writer.writerow(library_copy)

                        pair_id = (library_copy["scpca_library_id"], multiplexed_sample_id)
                        if pair_id not in combined_metadata_added_pair_ids:
                            combined_metadata_added_pair_ids.add(pair_id)
                            combined_metadata.append(library_copy)

        with open(self.output_multiplexed_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=ordered_fields, delimiter=common.TAB
            )
            project_csv_writer.writeheader()
            # Project file data has to be sorted by the library_id.
            project_csv_writer.writerows(
                sorted([cm for cm in combined_metadata], key=lambda cm: cm["scpca_library_id"])
            )

        return combined_metadata, multiplexed_sample_mapping

    def combine_single_cell_metadata(
        self,
        samples_metadata: List[Dict],
        single_cell_libraries_metadata: List[Dict],
        scpca_sample_ids: List[str],
    ):
        """Combines the two metadata dicts together to have all single cell data
        at the library level. Writes the combination out to the project and
        sample metadata files.
        """
        combined_metadata = list()

        if not single_cell_libraries_metadata:
            return combined_metadata

        # Get all the field names to pass to the csv.DictWriter
        all_fields = set(single_cell_libraries_metadata[0].keys())
        all_fields.update(
            set(samples_metadata[0].keys()) - set(self.output_single_cell_metadata_ignored_fields)
        )

        ordered_fields = self.output_single_cell_metadata_field_order
        all_fields -= set(ordered_fields)
        ordered_fields.extend(sorted(all_fields))  # The resulting field order.

        with open(self.output_single_cell_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=ordered_fields, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                    continue

                sample_metadata_copy = sample_metadata.copy()
                # Exclude fields.
                for field_name in self.output_single_cell_metadata_ignored_fields:
                    if field_name not in sample_metadata_copy:
                        continue
                    sample_metadata_copy.pop(field_name)

                sample_metadata_copy["pi_name"] = self.pi_name
                sample_metadata_copy["project_title"] = self.title
                sample_metadata_copy["scpca_project_id"] = self.scpca_id

                sample_metadata_path = Sample.get_output_single_cell_metadata_file_path(
                    scpca_sample_id
                )
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=ordered_fields, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    libraries = (
                        library
                        for library in single_cell_libraries_metadata
                        if library["scpca_sample_id"] == scpca_sample_id
                    )
                    for library in libraries:
                        library.update(sample_metadata_copy)
                        combined_metadata.append(library)

                        sample_csv_writer.writerow(library)
                        project_csv_writer.writerow(library)

        return combined_metadata

    def combine_spatial_metadata(
        self,
        samples_metadata: List[Dict],
        spatial_libraries_metadata: List[Dict],
        scpca_sample_ids: List[str],
    ):
        """Combines the two metadata dicts together to have all spatial data at
        the library level. Writes the combination out to the project and
        sample metadata files.
        """
        combined_metadata = list()

        if not spatial_libraries_metadata:
            return combined_metadata

        # Get all the field names to pass to the csv.DictWriter
        all_fields = set(spatial_libraries_metadata[0].keys())
        all_fields -= set(self.output_spatial_metadata_ignored_fields["library"])
        all_fields -= set(self.output_spatial_metadata_ignored_fields["single_cell"])
        all_fields.update(
            set(samples_metadata[0].keys())
            - set(self.output_spatial_metadata_ignored_fields["injected"])
        )

        ordered_fields = self.output_spatial_metadata_field_order
        all_fields -= set(ordered_fields)
        ordered_fields.extend(sorted(all_fields))  # The resulting field order.

        with open(self.output_spatial_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=ordered_fields, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                    continue

                sample_metadata_copy = sample_metadata.copy()
                # Exclude fields.
                field_names = (
                    self.output_spatial_metadata_ignored_fields["injected"]
                    + self.output_spatial_metadata_ignored_fields["single_cell"]
                )
                for field_name in field_names:
                    if field_name not in sample_metadata_copy:
                        continue
                    sample_metadata_copy.pop(field_name)

                sample_metadata_copy["pi_name"] = self.pi_name
                sample_metadata_copy["project_title"] = self.title
                sample_metadata_copy["scpca_project_id"] = self.scpca_id

                sample_metadata_path = Sample.get_output_spatial_metadata_file_path(scpca_sample_id)
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=ordered_fields, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    libraries = (
                        library
                        for library in spatial_libraries_metadata
                        if library["scpca_sample_id"] == scpca_sample_id
                    )
                    for library in libraries:
                        # Exclude fields.
                        for field_name in self.output_spatial_metadata_ignored_fields["library"]:
                            if field_name not in library:
                                continue
                            library.pop(field_name)

                        library.update(sample_metadata_copy)
                        combined_metadata.append(library)

                        sample_csv_writer.writerow(library)
                        project_csv_writer.writerow(library)

        return combined_metadata

    def create_computed_files(
        self,
        single_cell_file_mapping,
        single_cell_workflow_versions,
        spatial_file_mapping,
        spatial_workflow_versions,
        multiplexed_file_mapping,
        multiplexed_workflow_versions,
    ):
        """Creates project computed files based on generated file mappings."""
        computed_files = list()

        # The multiplexed and single cell cases are if/else as we produce
        # a single computed file for a multiplexed samples project.
        if multiplexed_file_mapping:
            computed_files.append(
                ComputedFile.create_project_multiplexed_file(
                    self, multiplexed_file_mapping, multiplexed_workflow_versions
                )
            )
        elif single_cell_file_mapping:
            computed_files.append(
                ComputedFile.create_project_single_cell_file(
                    self, single_cell_file_mapping, single_cell_workflow_versions
                )
            )
        if spatial_file_mapping:
            computed_files.append(
                ComputedFile.create_project_spatial_file(
                    self, spatial_file_mapping, spatial_workflow_versions
                )
            )

        return computed_files

    def create_single_cell_readme_file(self):
        """Creates a single cell metadata README file."""
        with open(ComputedFile.README_TEMPLATE_FILE_PATH, "r") as readme_template_file:
            readme_template = readme_template_file.read()
        with open(ComputedFile.README_FILE_PATH, "w") as readme_file:
            readme_file.write(
                readme_template.format(project_accession=self.scpca_id, project_url=self.url)
            )

    def create_multiplexed_readme_file(self):
        """Creates a multiplexed metadata README file."""
        with open(ComputedFile.README_TEMPLATE_MULTIPLEXED_FILE_PATH, "r") as readme_template_file:
            readme_template = readme_template_file.read()
        with open(ComputedFile.README_MULTIPLEXED_FILE_PATH, "w") as readme_file:
            readme_file.write(
                readme_template.format(project_accession=self.scpca_id, project_url=self.url)
            )

    def create_spatial_readme_file(self):
        """Creates a spatial metadata README file."""
        with open(ComputedFile.README_TEMPLATE_SPATIAL_FILE_PATH, "r") as readme_template_file:
            readme_template = readme_template_file.read()
        with open(ComputedFile.README_SPATIAL_FILE_PATH, "w") as readme_file:
            readme_file.write(
                readme_template.format(project_accession=self.scpca_id, project_url=self.url)
            )

    def get_bulk_rna_seq_sample_ids(self):
        """Returns bulk RNA sequencing sample IDs."""
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

    def get_sample_input_data_dir(self, sample_scpca_id):
        """Returns an input data directory based on a sample ID."""
        return os.path.join(self.input_data_dir, sample_scpca_id)

    def load_data(self, scpca_sample_ids=None) -> List[ComputedFile]:
        """
        Goes through a project directory contents, parses multiple level metadata
        files, writes combined metadata into resulting files.

        Returns a list of project's computed files.
        """

        # Start with a list of samples and their metadata.
        try:
            with open(self.input_samples_metadata_file_path) as samples_csv_file:
                samples_metadata = [line for line in csv.DictReader(samples_csv_file)]
        except FileNotFoundError:
            logger.error(f"No samples metadata file found for '{self}'.")
            return

        self.create_multiplexed_readme_file()
        self.create_single_cell_readme_file()
        self.create_spatial_readme_file()

        bulk_rna_seq_sample_ids = self.get_bulk_rna_seq_sample_ids()
        computed_files = list()
        non_downloadable_sample_ids = set()
        single_cell_libraries_metadata = list()
        spatial_libraries_metadata = list()
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                continue

            # Some samples will exist but their contents cannot be shared yet.
            # When this happens their corresponding sample folder will not exist.
            sample_dir = self.get_sample_input_data_dir(scpca_sample_id)
            if not os.path.exists(sample_dir):
                non_downloadable_sample_ids.add(scpca_sample_id)
                continue

            has_cite_seq_data = False
            has_spatial_data = False
            sample_cell_count_estimate = 0
            sample_seq_units = set()
            sample_technologies = set()
            for filename in os.listdir(sample_dir):
                # Handle single cell metadata.
                if filename.endswith("_metadata.json"):
                    with open(os.path.join(sample_dir, filename)) as sample_json_file:
                        sample_json = json.load(sample_json_file)

                    has_cite_seq_data = sample_json.get("has_citeseq", False)
                    sample_json["filtered_cell_count"] = sample_json.pop("filtered_cells")
                    sample_json["scpca_library_id"] = sample_json.pop("library_id")
                    sample_json["scpca_sample_id"] = sample_json.pop("sample_id")
                    single_cell_libraries_metadata.append(sample_json)

                    sample_cell_count_estimate += sample_json["filtered_cell_count"]
                    sample_seq_units.add(sample_json["seq_unit"].strip())
                    sample_technologies.add(sample_json["technology"].strip())

                # Handle spatial metadata.
                if self.has_spatial_data and filename.endswith("_spatial"):
                    spatial_dir = os.path.join(sample_dir, filename)
                    filename = filename.replace("spatial", "metadata.json")

                    with open(os.path.join(spatial_dir, filename)) as spatial_json_file:
                        spatial_json = json.load(spatial_json_file)

                    spatial_json["scpca_library_id"] = spatial_json.pop("library_id")
                    spatial_json["scpca_sample_id"] = spatial_json.pop("sample_id")
                    spatial_libraries_metadata.append(spatial_json)

                    has_spatial_data = True
                    sample_seq_units.add(spatial_json["seq_unit"].strip())
                    sample_technologies.add(spatial_json["technology"].strip())

            sample_metadata["has_bulk_rna_seq"] = scpca_sample_id in bulk_rna_seq_sample_ids
            sample_metadata["has_cite_seq_data"] = has_cite_seq_data
            sample_metadata["has_spatial_data"] = has_spatial_data
            sample_metadata["sample_cell_count_estimate"] = sample_cell_count_estimate
            sample_metadata["seq_units"] = ", ".join(sample_seq_units)
            sample_metadata["technologies"] = ", ".join(sample_technologies)

        multiplexed_libraries_metadata = list()
        multiplexed_sample_demux_cell_counter = Counter()
        multiplexed_library_path_mapping = dict()
        for multiplexed_sample_dir in Path(self.input_data_dir).rglob("*,*"):
            for filename in os.listdir(multiplexed_sample_dir):
                if not filename.endswith("_metadata.json"):
                    continue

                with open(os.path.join(multiplexed_sample_dir, filename)) as multiplexed_json_file:
                    multiplexed_json = json.load(multiplexed_json_file)

                library_id = multiplexed_json.pop("library_id")
                multiplexed_json["scpca_library_id"] = library_id
                multiplexed_json["scpca_sample_id"] = multiplexed_json.pop("sample_id")

                multiplexed_library_path_mapping[library_id] = multiplexed_sample_dir
                multiplexed_libraries_metadata.append(multiplexed_json)
                multiplexed_sample_demux_cell_counter.update(
                    multiplexed_json["sample_cell_estimates"]
                )

        combined_single_cell_metadata = self.combine_single_cell_metadata(
            samples_metadata, single_cell_libraries_metadata, scpca_sample_ids
        )

        combined_spatial_metadata = self.combine_spatial_metadata(
            samples_metadata, spatial_libraries_metadata, scpca_sample_ids
        )

        (
            combined_multiplexed_metadata,
            multiplexed_sample_mapping,
        ) = self.combine_multiplexed_metadata(
            samples_metadata, multiplexed_libraries_metadata, scpca_sample_ids
        )

        multiplexed_file_mapping = dict()
        multiplexed_workflow_versions = set()
        single_cell_file_mapping = dict()
        single_cell_workflow_versions = set()
        spatial_file_mapping = dict()
        spatial_workflow_versions = set()
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                continue

            sample_metadata[
                "demux_cell_count_estimate"
            ] = multiplexed_sample_demux_cell_counter.get(scpca_sample_id)
            sample_metadata["multiplexed_with"] = sorted(
                multiplexed_sample_mapping.get(scpca_sample_id, [])
            )

            sample = Sample.create_from_dict(sample_metadata, self)

            # Skip computed files creation if sample directory does not exist.
            if scpca_sample_id not in non_downloadable_sample_ids:
                libraries = [
                    library
                    for library in combined_single_cell_metadata
                    if library["scpca_sample_id"] == sample.scpca_id
                ]
                workflow_versions = [library["workflow_version"] for library in libraries]
                single_cell_workflow_versions.update(workflow_versions)
                (
                    computed_file,
                    single_cell_metadata_files,
                ) = ComputedFile.create_sample_single_cell_file(
                    sample, libraries, workflow_versions
                )
                computed_files.append(computed_file)
                single_cell_file_mapping.update(single_cell_metadata_files)

                if sample.has_spatial_data:
                    libraries = [
                        library
                        for library in combined_spatial_metadata
                        if library["scpca_sample_id"] == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    spatial_workflow_versions.update(workflow_versions)
                    (
                        computed_file,
                        spatial_metadata_files,
                    ) = ComputedFile.create_sample_spatial_file(
                        sample, libraries, workflow_versions
                    )
                    computed_files.append(computed_file)
                    spatial_file_mapping.update(spatial_metadata_files)

            if sample.has_multiplexed_data:
                libraries = [
                    library
                    for library in combined_multiplexed_metadata
                    if library.get("scpca_sample_id") == sample.scpca_id
                ]
                workflow_versions = [library["workflow_version"] for library in libraries]
                multiplexed_workflow_versions.update(workflow_versions)
                (
                    computed_file,
                    multiplexed_metadata_files,
                ) = ComputedFile.create_sample_multiplexed_file(
                    sample, libraries, multiplexed_library_path_mapping, workflow_versions
                )
                computed_files.append(computed_file)
                multiplexed_file_mapping.update(multiplexed_metadata_files)

        if multiplexed_file_mapping:
            # We want a single ZIP archive for a multiplexed samples project.
            multiplexed_file_mapping.update(single_cell_file_mapping)
            # Set project level flag for multiplexed data.
            self.has_multiplexed_data = True
            self.save(update_fields=("has_multiplexed_data",))

        computed_files.extend(
            self.create_computed_files(
                single_cell_file_mapping,
                single_cell_workflow_versions,
                spatial_file_mapping,
                spatial_workflow_versions,
                multiplexed_file_mapping,
                multiplexed_workflow_versions,
            )
        )

        self.update_counts()

        return computed_files

    def purge(self, delete_from_s3=False):
        """Purges project and its related data."""
        for sample in self.samples.all():
            for computed_file in sample.computed_files:
                if delete_from_s3:
                    computed_file.delete_s3_file(force=True)
                computed_file.delete()
            sample.delete()

        for computed_file in self.computed_files:
            if delete_from_s3:
                computed_file.delete_s3_file(force=True)
            computed_file.delete()

        ProjectSummary.objects.filter(project=self).delete()
        self.delete()

    def update_counts(self):
        """
        The Project and ProjectSummary models cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """

        additional_metadata_keys = set()
        diagnoses = set()
        diagnoses_counts = Counter()
        disease_timings = set()
        modalities = set()
        seq_units = set()
        summaries_counts = Counter()
        technologies = set()

        for sample in self.samples.all():
            additional_metadata_keys.update(sample.additional_metadata.keys())
            diagnoses.add(sample.diagnosis)
            disease_timings.add(sample.disease_timing)
            sample_seq_units = sample.seq_units.split(", ")
            sample_technologies = sample.technologies.split(", ")
            seq_units = seq_units.union(sample_seq_units)
            technologies = technologies.union(sample_technologies)

            if sample.has_cite_seq_data:
                modalities.add("CITE-seq")

            if sample.has_multiplexed_data:
                modalities.add("Multiplexed")

            if sample.has_spatial_data:
                modalities.add("Spatial Data")

            diagnoses_counts.update({sample.diagnosis: 1})
            for seq_unit in sample_seq_units:
                for technology in sample_technologies:
                    summaries_counts.update(
                        {(sample.diagnosis, seq_unit.strip(), technology.strip()): 1}
                    )

        diagnoses_strings = sorted(
            (f"{diagnosis} ({count})" for diagnosis, count in diagnoses_counts.items())
        )
        downloadable_sample_count = (
            self.samples.filter(sample_computed_files__isnull=False).distinct().count()
        )
        multiplexed_sample_count = self.samples.filter(has_multiplexed_data=True).distinct().count()
        seq_units = sorted((seq_unit for seq_unit in seq_units if seq_unit))
        technologies = sorted((technology for technology in technologies if technology))

        self.additional_metadata_keys = ", ".join(sorted(additional_metadata_keys))
        self.diagnoses = ", ".join(sorted(diagnoses))
        self.diagnoses_counts = ", ".join(diagnoses_strings)
        self.disease_timings = ", ".join(disease_timings)
        self.downloadable_sample_count = downloadable_sample_count
        self.modalities = ", ".join(sorted(modalities))
        self.multiplexed_sample_count = multiplexed_sample_count
        self.sample_count = self.samples.count()
        self.seq_units = ", ".join(seq_units)
        self.technologies = ", ".join(technologies)
        self.save()

        for (diagnosis, seq_unit, technology), count in summaries_counts.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=self, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count
            project_summary.save(update_fields=("sample_count",))
