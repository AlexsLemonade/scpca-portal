import csv
import json
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import Dict, List, Set

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.template.defaultfilters import pluralize
from django.template.loader import render_to_string

from scpca_portal import common, utils
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.contact import Contact
from scpca_portal.models.external_accession import ExternalAccession
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.publication import Publication
from scpca_portal.models.sample import Sample

logger = logging.getLogger()

IGNORED_INPUT_VALUES = {"", "N/A", "TBD"}
STRIPPED_INPUT_VALUES = "< >"


class Project(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    abstract = models.TextField()
    additional_metadata_keys = models.TextField(blank=True, null=True)
    additional_restrictions = models.TextField(blank=True, null=True)
    diagnoses = models.TextField(blank=True, null=True)
    diagnoses_counts = models.TextField(blank=True, null=True)
    disease_timings = models.TextField()
    downloadable_sample_count = models.IntegerField(default=0)
    has_multiplexed_data = models.BooleanField(default=False)
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
                type=ComputedFile.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def output_merged_computed_file_name(self):
        return f"{self.scpca_id}_merged.zip"

    @property
    def output_merged_anndata_computed_file_name(self):
        return f"{self.scpca_id}_merged_anndata.zip"

    @property
    def output_multiplexed_computed_file_name(self):
        return f"{self.scpca_id}_multiplexed.zip"

    @property
    def output_multiplexed_metadata_file_path(self):
        return common.OUTPUT_DATA_PATH / f"{self.scpca_id}_multiplexed_metadata.tsv"

    @property
    def output_single_cell_computed_file_name(self):
        return f"{self.scpca_id}.zip"

    @property
    def output_single_cell_anndata_computed_file_name(self):
        return f"{self.scpca_id}_anndata.zip"

    @property
    def output_single_cell_metadata_file_path(self):
        return common.OUTPUT_DATA_PATH / f"{self.scpca_id}_libraries_metadata.tsv"

    @property
    def output_spatial_computed_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_metadata_file_path(self):
        return common.OUTPUT_DATA_PATH / f"{self.scpca_id}_spatial_metadata.tsv"

    @property
    def single_cell_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                includes_merged=False,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_merged_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                includes_merged=True,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                includes_merged=False,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_merged_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                includes_merged=True,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
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

    def add_project_metadata(self, sample_metadata):
        """Adds project level metadata to the `sample_metadata`."""
        sample_metadata["pi_name"] = self.pi_name
        sample_metadata["project_title"] = self.title
        sample_metadata["scpca_project_id"] = self.scpca_id

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

    @staticmethod
    def process_computed_file(computed_file, clean_up_output_data, update_s3):
        """Processes saving, upload and cleanup of a single computed file."""
        logger.info(f"Processing {computed_file}")

        computed_file.save()
        if update_s3:
            logger.info(f"Uploading {computed_file}")
            computed_file.create_s3_file()

        # Don't clean up multiplexed sample zips until the project is done
        is_multiplexed_sample = computed_file.sample and computed_file.sample.has_multiplexed_data

        if clean_up_output_data and not is_multiplexed_sample:
            computed_file.zip_file_path.unlink(missing_ok=True)

        # Close DB connection for each thread.
        connection.close()

    def add_contacts(self, contact_email, contact_name):
        """Creates and adds project contacts."""
        emails = contact_email.split(common.CSV_MULTI_VALUE_DELIMITER)
        names = contact_name.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(emails) != len(names):
            logger.error("Unable to add ambiguous contacts.")
            return

        for idx, email in enumerate(emails):
            if email in IGNORED_INPUT_VALUES:
                continue

            contact, _ = Contact.objects.get_or_create(email=email.lower().strip())
            contact.name = names[idx].strip()
            contact.submitter_id = self.pi_name
            contact.save()

            self.contacts.add(contact)

    def add_external_accessions(
        self, external_accession, external_accession_url, external_accession_raw
    ):
        """Creates and adds project external accessions."""
        accessions = external_accession.split(common.CSV_MULTI_VALUE_DELIMITER)
        urls = external_accession_url.split(common.CSV_MULTI_VALUE_DELIMITER)
        accessions_raw = external_accession_raw.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(set((len(accessions), len(urls), len(accessions_raw)))) != 1:
            logger.error("Unable to add ambiguous external accessions.")
            return

        for idx, accession in enumerate(accessions):
            if accession in IGNORED_INPUT_VALUES:
                continue

            external_accession, _ = ExternalAccession.objects.get_or_create(
                accession=accession.strip()
            )
            external_accession.url = urls[idx].strip(STRIPPED_INPUT_VALUES)
            external_accession.has_raw = utils.boolean_from_string(accessions_raw[idx].strip())
            external_accession.save()

            self.external_accessions.add(external_accession)

    def add_publications(self, citation, citation_doi):
        """Creates and adds project publications."""
        citations = citation.split(common.CSV_MULTI_VALUE_DELIMITER)
        dois = citation_doi.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(citations) != len(dois):
            logger.error("Unable to add ambiguous publications.")
            return

        for idx, doi in enumerate(dois):
            if doi in IGNORED_INPUT_VALUES:
                continue

            publication, _ = Publication.objects.get_or_create(doi=doi.strip())
            publication.citation = citations[idx].strip(STRIPPED_INPUT_VALUES)
            publication.submitter_id = self.pi_name
            publication.save()

            self.publications.add(publication)

    def combine_single_cell_metadata(
        self,
        samples_metadata: List[Dict],
        single_cell_libraries_metadata: List[Dict],
        sample_id: str,
    ):
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

    def create_computed_files(
        self,
        single_cell_file_mapping,
        single_cell_workflow_versions,
        spatial_file_mapping,
        spatial_workflow_versions,
        multiplexed_file_mapping,
        multiplexed_workflow_versions,
        max_workers=8,  # 8 = 2 file formats * 4 mappings.
        clean_up_output_data=True,
        update_s3=False,
    ):
        """Prepares ready for saving project computed files based on generated file mappings."""

        def create_computed_file(future):
            computed_file = future.result()
            if computed_file:
                self.process_computed_file(computed_file, clean_up_output_data, update_s3)

        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for file_format in (
                ComputedFile.OutputFileFormats.ANN_DATA,
                ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            ):
                tasks.submit(
                    ComputedFile.get_project_merged_file,
                    self,
                    single_cell_file_mapping,
                    single_cell_workflow_versions,
                    file_format,
                ).add_done_callback(create_computed_file)

                if multiplexed_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_multiplexed_file,
                        self,
                        multiplexed_file_mapping,
                        multiplexed_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

                if single_cell_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_single_cell_file,
                        self,
                        single_cell_file_mapping,
                        single_cell_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

                if spatial_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_spatial_file,
                        self,
                        spatial_file_mapping,
                        spatial_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

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

    def get_additional_terms(self):
        if not self.additional_restrictions:
            return ""

        with open(
            common.TEMPLATE_PATH / "readme/additional_terms/research_academic_only.md"
        ) as additional_terms_file:
            return additional_terms_file.read()

    def get_demux_sample_ids(self) -> Set:
        demux_sample_ids = set()
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            multiplexed_sample_dir_demux_ids = multiplexed_sample_dir.name.split(',')
            demux_sample_ids.update(multiplexed_sample_dir_demux_ids)

        return demux_sample_ids

    def get_multiplexed_library_path_mapping(self) -> Dict:
        multiplexed_library_path_mapping = {}
        # Sort and iterate over multiplexed directories
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            # Sort and iterate over libraries within those directories
            for filename_path in sorted(Path(multiplexed_sample_dir).rglob("*_metadata.json")):
                library_id = filename_path.name.split('_')[0]
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
            "has_multiplexed_data",
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

    def get_sample_input_data_dir(self, sample_scpca_id):
        """Returns an input data directory based on a sample ID."""
        return self.input_data_path / sample_scpca_id

    def get_samples(
        self,
        samples_metadata,
        multiplexed_sample_demux_cell_counter,
        multiplexed_sample_mapping,
        multiplexed_sample_seq_units_mapping,
        multiplexed_sample_technologies_mapping,
        sample_id=None,
    ):
        """Prepares ready for saving sample objects."""
        samples = []
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if sample_id and scpca_sample_id != sample_id:
                continue
            sample_metadata[
                "demux_cell_count_estimate"
            ] = multiplexed_sample_demux_cell_counter.get(scpca_sample_id)
            sample_metadata["multiplexed_with"] = sorted(
                multiplexed_sample_mapping.get(scpca_sample_id, ())
            )
            sample_metadata["seq_units"] = (
                ", ".join(
                    sorted(
                        multiplexed_sample_seq_units_mapping.get(scpca_sample_id, ()), key=str.lower
                    )
                )
                or sample_metadata["seq_units"]
            )
            sample_metadata["technologies"] = (
                ", ".join(
                    sorted(
                        multiplexed_sample_technologies_mapping.get(scpca_sample_id, ()),
                        key=str.lower,
                    )
                )
                or sample_metadata["technologies"]
            )

            samples.append(Sample.get_from_dict(sample_metadata, self))

        return samples

    def load_data(self, sample_id=None, **kwargs) -> None:
        """
        Goes through a project directory's contents, parses multiple level metadata
        files, writes combined metadata into resulting files.

        Returns a list of project's computed files.
        """
        self.create_anndata_readme_file()
        self.create_anndata_merged_readme_file()
        self.create_multiplexed_readme_file()
        self.create_single_cell_readme_file()
        self.create_single_cell_merged_readme_file()
        self.create_spatial_readme_file()

        combined_metadata, updated_samples_metadata = self.handle_samples_metadata(sample_id)

        multiplexed_libraries_metadata = []
        multiplexed_sample_demux_cell_counter = Counter()
        multiplexed_sample_seq_units_mapping = {}
        multiplexed_sample_technologies_mapping = {}
        for multiplexed_sample_dir in sorted(Path(self.input_data_path).rglob("*,*")):
            for filename_path in sorted(Path(multiplexed_sample_dir).rglob("*_metadata.json")):
                with open(filename_path) as multiplexed_json_file:
                    multiplexed_json = json.load(multiplexed_json_file)

                multiplexed_json["scpca_library_id"] = multiplexed_json.pop("library_id")
                multiplexed_json["scpca_sample_id"] = multiplexed_json.pop("sample_id")

                multiplexed_libraries_metadata.append(multiplexed_json)
                multiplexed_sample_demux_cell_counter.update(
                    multiplexed_json["sample_cell_estimates"]
                )

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

        (
            combined_multiplexed_metadata,
            multiplexed_sample_mapping,
        ) = self.combine_multiplexed_metadata(
            updated_samples_metadata, multiplexed_libraries_metadata, sample_id
        )

        multiplexed_file_mapping = {
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        multiplexed_workflow_versions = set()
        single_cell_file_mapping = {
            ComputedFile.OutputFileFormats.ANN_DATA: {},
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        single_cell_workflow_versions = set()
        spatial_file_mapping = {
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        spatial_workflow_versions = set()

        samples = self.get_samples(
            updated_samples_metadata,
            multiplexed_sample_demux_cell_counter,
            multiplexed_sample_mapping,
            multiplexed_sample_seq_units_mapping,
            multiplexed_sample_technologies_mapping,
            sample_id=sample_id,
        )

        def update_ann_data(future):
            computed_file, metadata_files = future.result()
            single_cell_file_mapping[ComputedFile.OutputFileFormats.ANN_DATA].update(metadata_files)
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_multiplexed_data(future):
            computed_file, metadata_files = future.result()
            multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_single_cell_data(future):
            computed_file, metadata_files = future.result()
            single_cell_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_spatial_data(future):
            computed_file, metadata_files = future.result()
            spatial_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        non_downloadable_sample_ids = self.get_non_downloadable_sample_ids()
        max_workers = kwargs["max_workers"]
        samples_count = len(samples)
        logger.info(
            f"Processing {samples_count} sample{pluralize(samples_count)} using "
            f"{max_workers} worker{pluralize(max_workers)}"
        )

        # Prepare a threading.Lock for each multiplexed sample that shares a zip file.
        # The keys are the sample.multiplexed_ids since that will be unique across shared zip files.
        multiplexed_ids = set(
            ["_".join(s.multiplexed_ids) for s in samples if s.has_multiplexed_data]
        )
        locks = {multiplexed_ids: Lock() for multiplexed_ids in multiplexed_ids}

        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for sample in Sample.objects.bulk_create(samples):
                # Skip computed files creation if sample directory does not exist.
                if sample.scpca_id not in non_downloadable_sample_ids:
                    libraries = [
                        library
                        for library in combined_metadata[Sample.Modalities.SINGLE_CELL]
                        if library["scpca_sample_id"] == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    single_cell_workflow_versions.update(workflow_versions)

                    for file_format in sample.single_cell_file_formats:
                        tasks.submit(
                            ComputedFile.get_sample_single_cell_file,
                            sample,
                            libraries,
                            workflow_versions,
                            file_format,
                        ).add_done_callback(
                            update_single_cell_data
                            if file_format == ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT
                            else update_ann_data
                        )

                    if sample.has_spatial_data:
                        libraries = [
                            library
                            for library in combined_metadata[Sample.Modalities.SPATIAL]
                            if library["scpca_sample_id"] == sample.scpca_id
                        ]
                        workflow_versions = [library["workflow_version"] for library in libraries]
                        spatial_workflow_versions.update(workflow_versions)
                        tasks.submit(
                            ComputedFile.get_sample_spatial_file,
                            sample,
                            libraries,
                            workflow_versions,
                            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                        ).add_done_callback(update_spatial_data)

                if sample.has_multiplexed_data:
                    libraries = [
                        library
                        for library in combined_multiplexed_metadata
                        if library.get("scpca_sample_id") == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    multiplexed_workflow_versions.update(workflow_versions)

                    # Get the lock for current sample.
                    sample_lock = locks["_".join(sample.multiplexed_ids)]

                    tasks.submit(
                        ComputedFile.get_sample_multiplexed_file,
                        sample,
                        libraries,
                        self.get_multiplexed_library_path_mapping(),
                        workflow_versions,
                        ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                        lock=sample_lock,
                    ).add_done_callback(update_multiplexed_data)

        if multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT]:
            # We want a single ZIP archive for a multiplexed samples project.
            multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                single_cell_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT]
            )
        self.create_computed_files(
            single_cell_file_mapping,
            single_cell_workflow_versions,
            spatial_file_mapping,
            spatial_workflow_versions,
            multiplexed_file_mapping,
            multiplexed_workflow_versions,
            clean_up_output_data=kwargs["clean_up_output_data"],
            update_s3=kwargs["update_s3"],
        )

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

        self.update_counts()

    def handle_samples_metadata(self, sample_id=None):
        # Parses tsv sample metadata file, massages field names
        samples_metadata = self.load_samples_metadata()

        # Parses json library metadata files, massages field names, calculates aggregate values
        updated_samples_metadata, libraries_metadata = self.load_libraries_metadata(
            samples_metadata
        )

        # Combines samples and libraries metadata
        combined_metadata = self.combine_metadata(
            updated_samples_metadata, libraries_metadata, sample_id
        )

        return (combined_metadata, updated_samples_metadata)

    def load_samples_metadata(self) -> List[Dict]:
        # Start with a list of samples and their metadata.
        with open(self.input_samples_metadata_file_path) as samples_csv_file:
            samples_metadata = [sample for sample in csv.DictReader(samples_csv_file)]

        bulk_rna_seq_sample_ids = self.get_bulk_rna_seq_sample_ids()
        demux_sample_ids = self.get_demux_sample_ids()
        for sample_metadata in samples_metadata:
            sample_id = sample_metadata["scpca_sample_id"]

            # Some samples will exist but their contents cannot be shared yet.
            # When this happens their corresponding sample folder will not exist.
            sample_dir = self.get_sample_input_data_dir(sample_id)

            has_bulk_rna_seq = sample_id in bulk_rna_seq_sample_ids
            has_cite_seq_data = len(list(Path(sample_dir).glob("*_adt.*"))) > 0
            has_multiplexed_data = sample_id in demux_sample_ids
            has_single_cell_data = len(list(Path(sample_dir).glob("*_metadata.json"))) > 0
            has_spatial_data = len(list(Path(sample_dir).rglob("*_spatial/*_metadata.json"))) > 0
            include_anndata = len(list(Path(sample_dir).glob("*.hdf5"))) > 0

            sample_metadata["age_at_diagnosis"] = sample_metadata.pop("age")
            sample_metadata["has_bulk_rna_seq"] = has_bulk_rna_seq
            sample_metadata["has_cite_seq_data"] = has_cite_seq_data
            sample_metadata["has_multiplexed_data"] = has_multiplexed_data
            sample_metadata["has_single_cell_data"] = has_single_cell_data
            sample_metadata["has_spatial_data"] = has_spatial_data

            sample_metadata["includes_anndata"] = include_anndata

        return samples_metadata

    def load_libraries_metadata(self, samples_metadata: List[Dict]):

        libraries_metadata = {Sample.Modalities.SINGLE_CELL: [], Sample.Modalities.SPATIAL: []}

        updated_samples_metadata = samples_metadata.copy()

        for updated_sample_metadata in updated_samples_metadata:

            sample_dir = self.get_sample_input_data_dir(updated_sample_metadata["scpca_sample_id"])
            sample_cell_count_estimate = 0
            # sample_cell_count_estimate = Counter(count=0)
            sample_seq_units = set()
            sample_technologies = set()

            library_metadata_paths = sorted(
                list(Path(sample_dir).glob("*_metadata.json"))
                + list(Path(sample_dir).rglob("*_spatial/*_metadata.json"))
            )
            for filename_path in library_metadata_paths:
                with open(filename_path) as library_metadata_json_file:
                    library_json = json.load(library_metadata_json_file)

                library_json["scpca_library_id"] = library_json.pop("library_id")
                library_json["scpca_sample_id"] = library_json.pop("sample_id")

                if "filtered_cells" in library_json:
                    library_json["filtered_cell_count"] = library_json.pop("filtered_cells")
                    sample_cell_count_estimate += library_json["filtered_cell_count"]
                    # sample_cell_count_estimate.update(count=library_json["filtered_cell_count"])

                sample_seq_units.add(library_json["seq_unit"].strip())
                sample_technologies.add(library_json["technology"].strip())

                if "spatial" in str(filename_path):
                    libraries_metadata[Sample.Modalities.SPATIAL].append(library_json)
                else:
                    libraries_metadata[Sample.Modalities.SINGLE_CELL].append(library_json)

            updated_sample_metadata["sample_cell_count_estimate"] = sample_cell_count_estimate
            updated_sample_metadata["seq_units"] = ", ".join(
                sorted(sample_seq_units, key=str.lower)
            )
            updated_sample_metadata["technologies"] = ", ".join(
                sorted(sample_technologies, key=str.lower)
            )

        return (updated_samples_metadata, libraries_metadata)

    def combine_metadata(self, updated_samples_metadata, libraries_metadata, sample_id):
        combined_metadata = {Sample.Modalities.SINGLE_CELL: [], Sample.Modalities.SPATIAL: []}

        for modality in combined_metadata.keys():
            if not libraries_metadata[modality]:
                continue

            modalities = {modality}
            if modality is Sample.Modalities.SINGLE_CELL and self.has_cite_seq_data:
                modalities.add(Sample.Modalities.CITE_SEQ)

            library_metadata_keys = self.get_library_metadata_keys(
                set(libraries_metadata[modality][0].keys()), modalities=modalities
            )
            sample_metadata_keys = self.get_sample_metadata_keys(
                set(updated_samples_metadata[0].keys()), modalities=modalities
            )
            field_names = self.get_metadata_field_names(
                library_metadata_keys.union(sample_metadata_keys), modality=modality
            )

            project_metadata_path = f"output_{modality.lower()}_metadata_file_path"

            with open(getattr(self, project_metadata_path), "w", newline="") as project_file:
                project_csv_writer = csv.DictWriter(
                    project_file, fieldnames=field_names, delimiter=common.TAB
                )
                project_csv_writer.writeheader()

                for updated_sample_metadata in updated_samples_metadata:
                    scpca_sample_id = updated_sample_metadata["scpca_sample_id"]
                    if sample_id and scpca_sample_id != sample_id:
                        continue

                    updated_sample_metadata_copy = updated_sample_metadata.copy()
                    for key in updated_sample_metadata.keys():  # Exclude fields.
                        if key not in sample_metadata_keys:
                            updated_sample_metadata_copy.pop(key)

                    self.add_project_metadata(updated_sample_metadata_copy)

                    sample_metadata_path = Sample.get_output_metadata_file_path(
                        scpca_sample_id, modality
                    )
                    with open(sample_metadata_path, "w", newline="") as sample_file:
                        sample_csv_writer = csv.DictWriter(
                            sample_file, fieldnames=field_names, delimiter=common.TAB
                        )
                        sample_csv_writer.writeheader()

                        sample_libraries_metadata = (
                            library
                            for library in libraries_metadata[modality]
                            if library["scpca_sample_id"] == scpca_sample_id
                        )
                        for sample_library_metadata in sample_libraries_metadata:
                            sample_library_metadata_copy = sample_library_metadata.copy()
                            for key in sample_library_metadata.keys():  # Exclude fields.
                                if key not in library_metadata_keys:
                                    sample_library_metadata_copy.pop(key)

                            sample_library_combined_metadata = (
                                sample_library_metadata_copy | updated_sample_metadata_copy
                            )
                            combined_metadata[modality].append(sample_library_combined_metadata)

                            sample_csv_writer.writerow(sample_library_combined_metadata)
                            project_csv_writer.writerow(sample_library_combined_metadata)

        return combined_metadata

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
        downloadable_sample_count = (
            self.samples.filter(sample_computed_files__isnull=False).distinct().count()
        )
        multiplexed_sample_count = self.samples.filter(has_multiplexed_data=True).count()
        non_downloadable_samples_count = self.samples.filter(
            has_multiplexed_data=False, has_single_cell_data=False, has_spatial_data=False
        ).count()
        sample_count = self.samples.count()
        seq_units = sorted((seq_unit for seq_unit in seq_units if seq_unit))
        technologies = sorted((technology for technology in technologies if technology))
        unavailable_samples_count = max(
            sample_count - downloadable_sample_count - non_downloadable_samples_count, 0
        )

        if self.has_multiplexed_data and "multiplexed_with" in additional_metadata_keys:
            additional_metadata_keys.remove("multiplexed_with")

        self.additional_metadata_keys = ", ".join(sorted(additional_metadata_keys, key=str.lower))
        self.diagnoses = ", ".join(sorted(diagnoses))
        self.diagnoses_counts = ", ".join(diagnoses_strings)
        self.disease_timings = ", ".join(disease_timings)
        self.downloadable_sample_count = downloadable_sample_count
        self.modalities = sorted(modalities)
        self.multiplexed_sample_count = multiplexed_sample_count
        self.organisms = sorted(organisms)
        self.sample_count = sample_count
        self.seq_units = ", ".join(seq_units)
        self.technologies = ", ".join(technologies)
        self.unavailable_samples_count = unavailable_samples_count
        self.save()

        for (diagnosis, seq_unit, technology), count in summaries_counts.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=self, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count
            project_summary.save(update_fields=("sample_count",))
