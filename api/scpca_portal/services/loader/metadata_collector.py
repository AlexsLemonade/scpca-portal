import csv
import json
from typing import Dict, List
from collections import Counter
from pathlib import Path

from scpca_portal import common
from scpca_portal.models import Sample

from .metadata_file_paths import MetadataFilePaths

"""
The goal of this file is to extract Project and Sample metadata for input into the db.
As well, this file is responsible for aggregating desired fields for the necessary db input
(the typical aggregation use case is the aggregation of Sample data for use as Project totals).
"""
"""
Collect metadata from multiple files, and combine the collection into a single metadata file.
Additionally, save instances of project and samples into db.
"""


# Collect metadata from 3 sources
# Input sample and project info into db
# Create single output metadata files

class MetadataCollector():

    def collect_metadata(self, **kwargs):
        self.

    def extract_metadata(self):    
        self.process_project_data(**kwargs)
        # Start with a list of samples and their metadata.
        with open(MetadataFilePaths.input_samples_metadata_file_path) as samples_csv_file:
            samples_metadata = [line for line in csv.DictReader(samples_csv_file)]

        bulk_rna_seq_sample_ids = MetadataCollector.get_bulk_rna_seq_sample_ids()
        non_downloadable_sample_ids = set()
        single_cell_libraries_metadata = []
        spatial_libraries_metadata = []
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if sample_id and scpca_sample_id != sample_id:
                continue

            # Some samples will exist but their contents cannot be shared yet.
            # When this happens their corresponding sample folder will not exist.
            sample_dir = self.get_sample_input_data_dir(scpca_sample_id)
            if not sample_dir.exists():
                non_downloadable_sample_ids.add(scpca_sample_id)

            has_cite_seq_data = False
            has_single_cell_data = False
            has_spatial_data = False
            sample_cell_count_estimate = 0
            sample_seq_units = set()
            sample_technologies = set()
            # Handle single cell metadata.
            for filename_path in sorted(Path(sample_dir).glob("*_metadata.json")):
                with open(filename_path) as sample_json_file:
                    single_cell_json = json.load(sample_json_file)

                has_single_cell_data = True
                # Some rare samples can have one library with CITE-seq data and another library
                # next to it without CITE-seq data (e.g. SCPCP000008/SCPCS000368).
                has_cite_seq_data = single_cell_json.get("has_citeseq", False) or has_cite_seq_data

                single_cell_json["filtered_cell_count"] = single_cell_json.pop("filtered_cells")
                single_cell_json["scpca_library_id"] = single_cell_json.pop("library_id")
                single_cell_json["scpca_sample_id"] = single_cell_json.pop("sample_id")
                single_cell_libraries_metadata.append(single_cell_json)

                sample_cell_count_estimate += single_cell_json["filtered_cell_count"]
                sample_seq_units.add(single_cell_json["seq_unit"].strip())
                sample_technologies.add(single_cell_json["technology"].strip())

            # Handle spatial metadata.
            for filename_path in sorted(Path(sample_dir).rglob("*_spatial/*_metadata.json")):
                with open(filename_path) as spatial_json_file:
                    spatial_json = json.load(spatial_json_file)
                has_spatial_data = True

                spatial_json["scpca_library_id"] = spatial_json.pop("library_id")
                spatial_json["scpca_sample_id"] = spatial_json.pop("sample_id")
                spatial_libraries_metadata.append(spatial_json)

                sample_seq_units.add(spatial_json["seq_unit"].strip())
                sample_technologies.add(spatial_json["technology"].strip())

            sample_metadata["age_at_diagnosis"] = sample_metadata.pop("age")
            sample_metadata["has_bulk_rna_seq"] = scpca_sample_id in bulk_rna_seq_sample_ids
            sample_metadata["has_cite_seq_data"] = has_cite_seq_data
            sample_metadata["has_single_cell_data"] = has_single_cell_data
            sample_metadata["has_spatial_data"] = has_spatial_data
            sample_metadata["includes_anndata"] = len(list(Path(sample_dir).glob("*.hdf5"))) > 0
            sample_metadata["sample_cell_count_estimate"] = sample_cell_count_estimate
            sample_metadata["seq_units"] = ", ".join(sorted(sample_seq_units, key=str.lower))
            sample_metadata["technologies"] = ", ".join(sorted(sample_technologies, key=str.lower))

        multiplexed_libraries_metadata = []
        multiplexed_library_path_mapping = {}
        multiplexed_sample_demux_cell_counter = Counter()
        multiplexed_sample_seq_units_mapping = {}
        multiplexed_sample_technologies_mapping = {}
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            for filename_path in sorted(Path(multiplexed_sample_dir).rglob("*_metadata.json")):
                with open(filename_path) as multiplexed_json_file:
                    multiplexed_json = json.load(multiplexed_json_file)

                library_id = multiplexed_json.pop("library_id")
                multiplexed_json["scpca_library_id"] = library_id
                multiplexed_json["scpca_sample_id"] = multiplexed_json.pop("sample_id")

                multiplexed_library_path_mapping[library_id] = multiplexed_sample_dir
                multiplexed_libraries_metadata.append(multiplexed_json)
                multiplexed_sample_demux_cell_counter.update(
                    multiplexed_json["sample_cell_estimates"]
                )

                # Gather seq_units and technologies data.
                for demux_sample_id in multiplexed_json["demux_samples"]:
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

        combined_single_cell_metadata = self.combine_single_cell_metadata(
            samples_metadata, single_cell_libraries_metadata, sample_id
        )

        combined_spatial_metadata = self.combine_spatial_metadata(
            samples_metadata, spatial_libraries_metadata, sample_id
        )

        (
            combined_multiplexed_metadata,
            multiplexed_sample_mapping,
        ) = self.combine_multiplexed_metadata(
            samples_metadata, multiplexed_libraries_metadata, sample_id
        )

        samples = self.get_samples(
            samples_metadata,
            multiplexed_sample_demux_cell_counter,
            multiplexed_sample_mapping,
            multiplexed_sample_seq_units_mapping,
            multiplexed_sample_technologies_mapping,
            sample_id=sample_id,
        )

        Sample.objects.bulk_create(samples)

        self.project.update_counts()

        return (
            combined_single_cell_metadata,
            combined_spatial_metadata,
            combined_multiplexed_metadata
        )


    def add_project_metadata(self, sample_metadata):
        """Adds project level metadata to the `sample_metadata`."""
        sample_metadata["pi_name"] = self.pi_name
        sample_metadata["project_title"] = self.title
        sample_metadata["scpca_project_id"] = self.scpca_id

    def combine_single_cell_metadata(
        self,
        samples_metadata: List[Dict],
        single_cell_libraries_metadata: List[Dict],
        sample_id: str,
    ) -> List[Dict]:
        """Combines the two metadata dicts together to have all single cell data
        at the library level. Writes the combination out to the project and
        sample metadata files.
        """
        combined_metadata = []

        if not single_cell_libraries_metadata:
            return combined_metadata

        modality = Sample.Modalities.SINGLE_CELL
        modalities = {modality}
        if self.has_cite_seq_data:
            modalities.add(Sample.Modalities.CITE_SEQ)

        library_metadata_keys = self.get_library_metadata_keys(
            set(single_cell_libraries_metadata[0].keys()), modalities=modalities
        )
        sample_metadata_keys = self.get_sample_metadata_keys(
            set(samples_metadata[0].keys()), modalities=modalities
        )
        field_names = self.get_metadata_field_names(
            library_metadata_keys.union(sample_metadata_keys), modality=modality
        )

        with open(self.output_single_cell_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=field_names, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if sample_id and scpca_sample_id != sample_id:
                    continue

                sample_metadata_copy = sample_metadata.copy()
                for key in sample_metadata.keys():  # Exclude fields.
                    if key not in sample_metadata_keys:
                        sample_metadata_copy.pop(key)

                self.add_project_metadata(sample_metadata_copy)

                sample_metadata_path = Sample.get_output_metadata_file_path(
                    scpca_sample_id, modality
                )
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=field_names, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    libraries_metadata = (
                        library
                        for library in single_cell_libraries_metadata
                        if library["scpca_sample_id"] == scpca_sample_id
                    )
                    for library_metadata in libraries_metadata:
                        library_metadata_copy = library_metadata.copy()
                        for key in library_metadata.keys():  # Exclude fields.
                            if key not in library_metadata_keys:
                                library_metadata_copy.pop(key)

                        library_metadata_copy.update(sample_metadata_copy)
                        combined_metadata.append(library_metadata_copy)

                        sample_csv_writer.writerow(library_metadata_copy)
                        project_csv_writer.writerow(library_metadata_copy)

        return combined_metadata

    def combine_spatial_metadata(
        self,
        samples_metadata: List[Dict],
        spatial_libraries_metadata: List[Dict],
        sample_id: str,
    ):
        """Combines the two metadata dicts together to have all spatial data at
        the library level. Writes the combination out to the project and
        sample metadata files.
        """
        combined_metadata = []

        if not spatial_libraries_metadata:
            return combined_metadata

        modality = Sample.Modalities.SPATIAL
        library_metadata_keys = self.get_library_metadata_keys(
            set(spatial_libraries_metadata[0].keys()), modalities={modality}
        )
        sample_metadata_keys = self.get_sample_metadata_keys(
            set(samples_metadata[0].keys()), modalities={modality}
        )
        field_names = self.get_metadata_field_names(
            library_metadata_keys.union(sample_metadata_keys), modality=modality
        )

        with open(self.output_spatial_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=field_names, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if sample_id and scpca_sample_id != sample_id:
                    continue

                sample_metadata_copy = sample_metadata.copy()
                for key in sample_metadata.keys():  # Exclude fields.
                    if key not in sample_metadata_keys:
                        sample_metadata_copy.pop(key)

                self.add_project_metadata(sample_metadata_copy)

                sample_metadata_path = Sample.get_output_metadata_file_path(
                    scpca_sample_id, modality
                )
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=field_names, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    libraries_metadata = (
                        library
                        for library in spatial_libraries_metadata
                        if library["scpca_sample_id"] == scpca_sample_id
                    )
                    for library_metadata in libraries_metadata:
                        library_metadata_copy = library_metadata.copy()
                        for key in library_metadata.keys():  # Exclude fields.
                            if key not in library_metadata_keys:
                                library_metadata_copy.pop(key)

                        library_metadata_copy.update(sample_metadata_copy)
                        combined_metadata.append(library_metadata_copy)

                        sample_csv_writer.writerow(library_metadata_copy)
                        project_csv_writer.writerow(library_metadata_copy)

        return combined_metadata

    def combine_multiplexed_metadata(
        self,
        samples_metadata: List[Dict],
        multiplexed_libraries_metadata: List[Dict],
        sample_id: str,
    ):
        """Combines the two metadata dicts together to have all multiplexed data
        at the library level. Writes the combination out to the project and
        sample metadata files. The sample file also includes multiplexed samples.
        """

        combined_metadata = []
        multiplexed_sample_mapping = {}
        if not multiplexed_libraries_metadata:
            return combined_metadata, multiplexed_sample_mapping

        modality = Sample.Modalities.MULTIPLEXED
        library_metadata_keys = self.get_library_metadata_keys(
            set(multiplexed_libraries_metadata[0].keys()), modalities={modality}
        )
        sample_metadata_keys = self.get_sample_metadata_keys(
            set(samples_metadata[0].keys()), modalities={modality}
        )
        field_names = self.get_metadata_field_names(
            library_metadata_keys.union(sample_metadata_keys), modality=modality
        )

        multiplexed_library_mapping = {}  # Sample ID to library IDs mapping.
        multiplexed_sample_ids = set()  # Unified multiplexed sample ID set.
        for library_metadata in multiplexed_libraries_metadata:
            multiplexed_library_sample_ids = library_metadata["demux_samples"]
            for multiplexed_sample_id in multiplexed_library_sample_ids:
                # Populate multiplexed library mapping.
                if multiplexed_sample_id not in multiplexed_library_mapping:
                    multiplexed_library_mapping[multiplexed_sample_id] = set()
                multiplexed_library_mapping[multiplexed_sample_id].add(
                    library_metadata["scpca_library_id"]
                )

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
        sample_metadata_mapping = {}
        for sample_metadata in samples_metadata:
            multiplexed_sample_id = sample_metadata["scpca_sample_id"]
            if multiplexed_sample_id not in multiplexed_sample_ids:  # Skip non-multiplexed samples.
                continue

            if sample_id and multiplexed_sample_id != sample_id:
                continue

            sample_metadata_copy = sample_metadata.copy()
            for key in sample_metadata.keys():  # Exclude fields.
                if key not in sample_metadata_keys:
                    sample_metadata_copy.pop(key)

            self.add_project_metadata(sample_metadata_copy)
            sample_metadata_mapping[multiplexed_sample_id] = sample_metadata_copy

        # Combine and write the metadata.
        combined_metadata_added_pair_ids = set()
        for sample_id in sorted(sample_metadata_mapping.keys()):
            sample_metadata_path = Sample.get_output_metadata_file_path(sample_id, modality)
            with open(sample_metadata_path, "w", newline="") as sample_file:
                sample_csv_writer = csv.DictWriter(
                    sample_file, fieldnames=field_names, delimiter=common.TAB
                )
                sample_csv_writer.writeheader()

                multiplexed_sample_ids = sorted(multiplexed_sample_mapping[sample_id])
                multiplexed_sample_ids.insert(0, sample_id)  # Current sample libraries go first.
                for multiplexed_sample_id in multiplexed_sample_ids:
                    libraries_metadata = sorted(
                        (
                            library
                            for library in multiplexed_libraries_metadata
                            if library["scpca_library_id"] in multiplexed_library_mapping[sample_id]
                        ),
                        key=lambda library: library["scpca_library_id"],
                    )
                    for library_metadata in libraries_metadata:
                        library_metadata_copy = library_metadata.copy()
                        for key in library_metadata.keys():  # Exclude fields.
                            if key not in library_metadata_keys:
                                library_metadata_copy.pop(key)

                        library_metadata_copy.update(
                            sample_metadata_mapping.get(multiplexed_sample_id, {})
                        )
                        sample_csv_writer.writerow(library_metadata_copy)

                        pair_id = (library_metadata_copy["scpca_library_id"], multiplexed_sample_id)
                        if pair_id not in combined_metadata_added_pair_ids:
                            combined_metadata_added_pair_ids.add(pair_id)
                            combined_metadata.append(library_metadata_copy)

        with open(self.output_multiplexed_metadata_file_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=field_names, delimiter=common.TAB
            )
            project_csv_writer.writeheader()
            # Project file data has to be sorted by the library_id.
            project_csv_writer.writerows(
                sorted([cm for cm in combined_metadata], key=lambda cm: cm["scpca_library_id"])
            )

        return combined_metadata, multiplexed_sample_mapping

    def get_bulk_rna_seq_sample_ids(self):
        """Returns bulk RNA sequencing sample IDs."""
        bulk_rna_seq_sample_ids = set()
        if self.has_bulk_rna_seq:
            with open(MetadataFilePaths.input_bulk_metadata_file_path, "r") as bulk_metadata_file:
                bulk_rna_seq_sample_ids.update(
                    (
                        line["sample_id"]
                        for line in csv.DictReader(bulk_metadata_file, delimiter=common.TAB)
                    )
                )
        return bulk_rna_seq_sample_ids

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

    def get_metadata_field_names(self, columns, modality):
        """Returns a list of metadata field names based on the modality context."""
        ordering = {
            Sample.Modalities.MULTIPLEXED: (
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
                "age_at_diagnosis",
                "sex",
                "tissue_location",
                "treatment",
                "participant_id",
                "submitter",
                "submitter_id",
            ),
            Sample.Modalities.SINGLE_CELL: (
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
                "age_at_diagnosis",
                "sex",
                "tissue_location",
            ),
            Sample.Modalities.SPATIAL: (
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
                "age_at_diagnosis",
                "sex",
                "tissue_location",
                "treatment",
                "participant_id",
                "submitter",
                "submitter_id",
            ),
        }

        return sorted(
            sorted((c for c in columns), key=str.lower),  # Sort by a column name first.
            key=lambda k: (
                ordering[modality].index(k)  # Then enforce expected ordering.
                if k in ordering[modality]
                else float("inf")
            ),
        )

    def get_sample_metadata_keys(self, all_keys, modalities=()):
        """Returns a set of metadata keys based on the modalities context."""
        excluded_keys = {
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_single_cell_data",
            "has_spatial_data",
            "seq_units",
            "technologies",
        }
        project_keys = {
            "pi_name",
            "project_title",
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

        return all_keys.union(project_keys).difference(excluded_keys)

    def process_project_data(self, **kwargs):
        project_samples_mapping = {
            project_path.name: set((sd.name for sd in project_path.iterdir() if sd.is_dir()))
            for project_path in common.INPUT_DATA_PATH.iterdir()
            if project_path.is_dir()
        }

        with open(Project.get_input_project_metadata_file_path()) as project_csv:
            project_list = list(csv.DictReader(project_csv))

        for project_data in project_list:
            scpca_project_id = project_data["scpca_project_id"]
            if project_id and project_id != scpca_project_id:
                continue

            if scpca_project_id not in project_samples_mapping:
                logger.warning(
                    f"Metadata found for '{scpca_project_id}' but no s3 folder of that name exists."
                )
                return

            if project_data["submitter"] not in allowed_submitters:
                logger.warning("Project submitter  is not the white list.")
                continue

            # Purge existing projects so they can be re-added.
            if (project := Project.objects.filter(scpca_id=scpca_project_id).first()) and (
                kwargs["reload_all"] or kwargs["reload_existing"]
            ):
                logger.info(f"Purging '{project}")
                project.purge(delete_from_s3=kwargs["update_s3"])

            # Only import new projects. If old ones are desired they should be purged and re-added.
            project, created = Project.objects.get_or_create(scpca_id=scpca_project_id)
            if not created:
                logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
                continue

            self.project = Project.objects.filter(scpca_id=scpca_project_id).first()
            logger.info(f"Importing '{self.project}' data")

            self.project.abstract = project_data["abstract"]
            self.project.additional_restrictions = project_data["additional_restrictions"]
            self.project.has_bulk_rna_seq = utils.boolean_from_string(project_data.get("has_bulk", False))
            self.project.has_cite_seq_data = utils.boolean_from_string(project_data.get("has_CITE", False))
            self.project.has_multiplexed_data = utils.boolean_from_string(
                project_data.get("has_multiplex", False)
            )
            self.project.has_spatial_data = utils.boolean_from_string(data.get("has_spatial", False))
            self.project.human_readable_pi_name = data["PI"]
            self.project.includes_anndata = utils.boolean_from_string(
                project_data.get("includes_anndata", False)
            )
            self.project.includes_cell_lines = utils.boolean_from_string(
                project_data.get("includes_cell_lines", False)
            )
            self.project.includes_xenografts = utils.boolean_from_string(
                project_data.get("includes_xenografts", False)
            )
            self.project.pi_name = project_data["submitter"]
            self.project.title = project_data["project_title"]
            self.project.save()

            self.project.add_contacts(project_data["contact_email"], project_data["contact_name"])
            self.project.add_external_accessions(
                project_data["external_accession"],
                project_data["external_accession_url"],
                project_data["external_accession_raw"],
            )
            self.project.add_publications(project_data["citation"], project_data["citation_doi"])
