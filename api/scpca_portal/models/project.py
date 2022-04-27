import csv
import json
import logging
import os
from pathlib import Path
from typing import Dict, List
from zipfile import ZipFile

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from scpca_portal import common
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.sample import Sample

logger = logging.getLogger()


class Project(models.Model):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    # TODO(arkid15r): extract to an abstact model.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    has_spatial_data = models.BooleanField(default=False)
    human_readable_pi_name = models.TextField(null=False)
    modalities = models.TextField(blank=True, null=True)
    pi_name = models.TextField(null=False)
    sample_count = models.IntegerField(default=0)
    scpca_id = models.TextField(unique=True, null=False)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    title = models.TextField(null=False)

    def __str__(self):
        return f"Project {self.scpca_id}"

    @staticmethod
    def get_input_metadata_path():
        return os.path.join(common.INPUT_DATA_DIR, "project_metadata.csv")

    # TODO(arkid15r): remove the property after BE/FE refactoring.
    @property
    def computed_file(self):
        return self.project_computed_file.first()

    @property
    def input_data_dir(self):
        return os.path.join(common.INPUT_DATA_DIR, self.scpca_id)

    @property
    def input_bulk_metadata_path(self):
        return os.path.join(self.input_data_dir, f"{self.scpca_id}_bulk_metadata.tsv")

    @property
    def input_bulk_quant_path(self):
        return os.path.join(self.input_data_dir, f"{self.scpca_id}_bulk_quant.tsv")

    @property
    def input_samples_metadata_path(self):
        return os.path.join(self.input_data_dir, "samples_metadata.csv")

    @property
    def output_single_cell_data_file_name(self):
        return f"{self.scpca_id}.zip"

    @property
    def output_single_cell_data_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, self.output_single_cell_data_file_name)

    @property
    def output_spatial_data_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_data_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, self.output_spatial_data_file_name)

    @property
    def output_single_cell_metadata_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{self.scpca_id}_libraries_metadata.tsv")

    @property
    def output_spatial_metadata_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{self.scpca_id}_spatial_metadata.tsv")

    @property
    def url(self):
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"

    def combine_single_cell_metadata(
        self,
        samples_metadata: List[Dict],
        single_cell_libraries_metadata: List[Dict],
        scpca_sample_ids: List[str],
    ):
        """Combines the two metadata dicts together to have all single cell data
        at the library level. Writes the combination out at the project and
        sample level.
        """
        combined_metadata = []

        # Get all the field names to pass to the csv.DictWriter
        field_names = list(single_cell_libraries_metadata[0].keys()) + list(
            samples_metadata[0].keys()
        )
        field_names += ("scpca_project_id", "pi_name", "project_title")  # Additional fields.

        field_order = [
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "seq_unit",
            "technology",
            "cell_count",
            "scpca_project_id",
            "pi_name",
            "project_title",
            "disease_timing",
            "age",
            "sex",
            "tissue_location",
        ]

        # Manually injected fields to be removed from the sample level.
        sample_metadata_excluded_field_names = ("seq_units", "technologies")

        field_names = set(field_names)
        field_names -= set(field_order)
        field_names -= set(sample_metadata_excluded_field_names)

        # The resulting field order.
        field_order.extend(sorted(field_names))

        with open(self.output_single_cell_metadata_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=field_order, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                    continue

                sample_metadata_copy = sample_metadata.copy()

                # Remove excluded fields.
                for excluded_field_name in sample_metadata_excluded_field_names:
                    if excluded_field_name not in sample_metadata_copy:
                        continue
                    sample_metadata_copy.pop(excluded_field_name)

                sample_metadata_copy["pi_name"] = self.pi_name
                sample_metadata_copy["project_title"] = self.title
                sample_metadata_copy["scpca_project_id"] = self.scpca_id

                sample_metadata_path = Sample.get_output_metadata_path(scpca_sample_id)
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=field_order, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    for library in single_cell_libraries_metadata:
                        if library["scpca_sample_id"] != scpca_sample_id:
                            continue

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
        the library level. Writes the combination out at the project and
        sample level.
        """
        combined_metadata = []

        # Get all the field names to pass to the csv.DictWriter
        field_names = list(spatial_libraries_metadata[0].keys()) + list(samples_metadata[0].keys())

        field_order = [
            "scpca_project_id",
            "scpca_sample_id",  # From spatial file.
            "scpca_library_id",  # From spatial file.
            "technology",  # From spatial file.
            "seq_unit",  # From spatial file.
            "total_reads",  # From spatial file.
            "mapped_reads",  # From spatial file.
            "genome_assembly",
            "mapping_index",  # From spatial file.
            "date_processed",
            "spaceranger_version",
            "workflow",  # From spatial file.
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
            "BRAF_status",
            "spinal_leptomeningeal_mets",
        ]

        single_cell_excluded_field_names = (
            "alevin_fry_version",
            "cell_count",
            "filtered_cell_count",
            "filtering_method",
            "has_citeseq",
            "salmon_version",
            "seq_units",
            "technologies",
            "transcript_type",
            "unfiltered_cells",
            "workflow_version",
        )

        single_cell_suppressed_field_names = (
            "mapped_reads",
            "mapping_index",
            "scpca_library_id",
            "scpca_sample_id",
            "seq_unit",
            "seq_units",
            "technologies",
            "technology",
            "total_reads",
            "workflow",
            "workflow_commit",
            "date_processed",
        )

        spatial_excluded_field_names = (
            "filtered_spots",
            "tissue_spots",
            "unfiltered_spots",
        )

        field_names = set(field_names)
        field_names -= set(single_cell_excluded_field_names)
        field_names -= set(single_cell_suppressed_field_names)
        field_names -= set(spatial_excluded_field_names)
        field_names -= set(field_order)

        # The resulting field order.
        field_order.extend(sorted(field_names))

        with open(self.output_spatial_metadata_path, "w", newline="") as project_file:
            project_csv_writer = csv.DictWriter(
                project_file, fieldnames=field_order, delimiter=common.TAB
            )
            project_csv_writer.writeheader()

            for sample_metadata in samples_metadata:
                scpca_sample_id = sample_metadata["scpca_sample_id"]
                if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                    continue

                sample_metadata_copy = sample_metadata.copy()

                # Remove excluded/suppressed fields.
                field_names = single_cell_excluded_field_names + single_cell_suppressed_field_names
                for field_name in field_names:
                    if field_name not in sample_metadata_copy:
                        continue
                    sample_metadata_copy.pop(field_name)

                sample_metadata_copy["pi_name"] = self.pi_name
                sample_metadata_copy["project_title"] = self.title
                sample_metadata_copy["scpca_project_id"] = self.scpca_id

                sample_metadata_path = Sample.get_output_spatial_metadata_path(scpca_sample_id)
                with open(sample_metadata_path, "w", newline="") as sample_file:
                    sample_csv_writer = csv.DictWriter(
                        sample_file, fieldnames=field_order, delimiter=common.TAB
                    )
                    sample_csv_writer.writeheader()

                    for library in spatial_libraries_metadata:
                        if library["scpca_sample_id"] != scpca_sample_id:
                            continue

                        # Remove excluded fields.
                        for excluded_field_name in spatial_excluded_field_names:
                            if excluded_field_name not in library:
                                continue
                            library.pop(excluded_field_name)

                        library.update(sample_metadata_copy)
                        combined_metadata.append(library)

                        sample_csv_writer.writerow(library)
                        project_csv_writer.writerow(library)

        return combined_metadata

    def create_single_cell_data_file(self, sample_to_file_mapping: dict) -> ComputedFile:
        """Produces a single data file of combined single cell data."""

        computed_file = ComputedFile(
            prjct=self,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=self.output_single_cell_data_file_name,
            type=ComputedFile.FileTypes.PROJECT_ZIP,
            workflow_version="",
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(ComputedFile.README_FILE_PATH, ComputedFile.README_FILE_NAME)
            zip_file.write(self.output_single_cell_metadata_path, computed_file.metadata_file_name)

            for sample_id, file_paths in sample_to_file_mapping.items():
                for file_path in file_paths:
                    # Nest these under thier sample id.
                    archive_path = os.path.join(sample_id, os.path.basename(file_path))
                    zip_file.write(file_path, archive_path)

            if self.has_bulk_rna_seq:
                zip_file.write(self.input_bulk_metadata_path, "bulk_metadata.tsv")
                zip_file.write(self.input_bulk_quant_path, "bulk_quant.tsv")

        computed_file.size_in_bytes = os.path.getsize(computed_file.zip_file_path)
        computed_file.save()

        return computed_file

    def create_spatial_data_file(self, sample_to_file_mapping: dict) -> ComputedFile:
        """Produces a data file of combined spatial data."""

        computed_file = ComputedFile(
            prjct=self,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=self.output_spatial_data_file_name,
            type=ComputedFile.FileTypes.PROJECT_SPATIAL_ZIP,
            workflow_version="",
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(ComputedFile.README_FILE_PATH, ComputedFile.README_FILE_NAME)
            zip_file.write(self.output_spatial_metadata_path, computed_file.metadata_file_name)

            for sample_id, file_paths in sample_to_file_mapping.items():
                sample_path = Path(self.get_sample_input_data_dir(sample_id))
                for file_path in file_paths:
                    zip_file.write(file_path, Path(file_path).relative_to(sample_path))

        computed_file.size_in_bytes = os.path.getsize(computed_file.zip_file_path)
        computed_file.save()

        return computed_file

    def get_sample_input_data_dir(self, scpca_id):
        return os.path.join(self.input_data_dir, scpca_id)

    def load_data(self, scpca_sample_ids=None) -> List[ComputedFile]:
        """
        Goes through a project directory contents, parses multiple level metadata
        files, writes combined metadata into resulting files.

        Returns a list of project's computed files.
        """

        # Create readme file first.
        with open(ComputedFile.README_TEMPLATE_FILE_PATH, "r") as readme_template_file:
            readme_template = readme_template_file.read()
        with open(ComputedFile.README_FILE_PATH, "w") as readme_file:
            readme_file.write(
                readme_template.format(project_accession=self.scpca_id, project_url=self.url)
            )

        # Start with a list of samples and their metadata.
        try:
            with open(self.input_samples_metadata_path) as samples_csv_file:
                samples_metadata = [line for line in csv.DictReader(samples_csv_file)]
        except FileNotFoundError:
            logger.error(f"No samples metadata file found for '{self}'.")
            return

        computed_files = []
        single_cell_libraries_metadata = []
        spatial_libraries_metadata = []
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if scpca_sample_ids and scpca_sample_id not in scpca_sample_ids:
                continue

            # Some samples will exist but their contents cannot be shared yet.
            # When this happens their corresponding sample folder will not exist.
            sample_dir = self.get_sample_input_data_dir(scpca_sample_id)
            if not os.path.exists(sample_dir):
                continue

            sample_cell_count = 0
            sample_seq_units = set()
            sample_technologies = set()
            for filename in os.listdir(sample_dir):
                # Handle sample metadata.
                if filename.endswith("_metadata.json"):
                    with open(os.path.join(sample_dir, filename)) as sample_json_file:
                        sample_json = json.load(sample_json_file)
                        sample_json["scpca_sample_id"] = sample_json.pop("sample_id")
                        sample_json["scpca_library_id"] = sample_json.pop("library_id")
                        sample_json["filtered_cell_count"] = sample_json.pop("filtered_cells")
                        single_cell_libraries_metadata.append(sample_json)

                        sample_metadata["workflow_version"] = sample_json["workflow_version"]
                        sample_cell_count += sample_json["filtered_cell_count"]
                        sample_seq_units.add(sample_json["seq_unit"].strip())
                        sample_technologies.add(sample_json["technology"].strip())

                # Handle spatial metadata.
                if self.has_spatial_data and filename.endswith("_spatial"):
                    spatial_dir = os.path.join(sample_dir, filename)
                    spatial_json_filename = filename.replace("spatial", "metadata.json")

                    with open(
                        os.path.join(spatial_dir, spatial_json_filename)
                    ) as spatial_json_file:
                        spatial_json = json.load(spatial_json_file)
                        spatial_json["scpca_sample_id"] = spatial_json.pop("sample_id")
                        spatial_json["scpca_library_id"] = spatial_json.pop("library_id")
                        spatial_libraries_metadata.append(spatial_json)

                        sample_seq_units.add(spatial_json["seq_unit"].strip())
                        sample_technologies.add(spatial_json["technology"].strip())

            sample_metadata["cell_count"] = sample_cell_count
            sample_metadata["seq_units"] = ", ".join(sample_seq_units)
            sample_metadata["technologies"] = ", ".join(sample_technologies)

        combined_single_cell_metadata = self.combine_single_cell_metadata(
            samples_metadata, single_cell_libraries_metadata, scpca_sample_ids
        )

        if self.has_spatial_data:
            combined_spatial_metadata = self.combine_spatial_metadata(
                samples_metadata, spatial_libraries_metadata, scpca_sample_ids
            )

        single_cell_file_mapping = {}
        spatial_file_mapping = {}
        for sample_metadata in samples_metadata:
            if scpca_sample_ids and sample_metadata["scpca_sample_id"] not in scpca_sample_ids:
                continue

            workflow_version = sample_metadata.pop("workflow_version")
            sample = Sample.create_from_dict(sample_metadata, self)

            computed_file, single_cell_metadata_files = sample.create_single_cell_data_file(
                combined_single_cell_metadata, workflow_version
            )
            computed_files.append(computed_file)
            single_cell_file_mapping.update(single_cell_metadata_files)

            if self.has_spatial_data:
                computed_file, spatial_metadata_files = sample.create_spatial_data_file(
                    combined_spatial_metadata, workflow_version,
                )
                computed_files.append(computed_file)
                spatial_file_mapping.update(spatial_metadata_files)

        computed_files.append(self.create_single_cell_data_file(single_cell_file_mapping))
        if self.has_spatial_data:
            computed_files.append(self.create_spatial_data_file(spatial_metadata_files))

        return computed_files

    def purge(self, delete_from_s3=False):
        """Purges project and its related data."""
        for sample in self.samples.all():
            if sample.computed_file:
                if delete_from_s3:
                    sample.computed_file.delete_s3_file(force=True)
                sample.computed_file.delete()
            sample.delete()

        if self.computed_file:
            if delete_from_s3:
                self.computed_file.delete_s3_file(force=True)
            self.computed_file.delete()

        ProjectSummary.objects.filter(project=self).delete()
        self.delete()

    @receiver(post_save, sender="scpca_portal.Sample")
    def update_project_counts(sender, instance, created=False, update_fields=None, **kwargs):
        """The Project and ProjectSummary models cache aggregated sample metadata.

        When Samples are added to the Project, we need to update these."""

        project = instance.project

        additional_metadata_keys = set()
        diagnoses = set()
        diagnoses_counts = {}
        disease_timings = set()
        modalities = set()
        seq_units = set()
        summaries = {}
        technologies = set()

        for sample in project.samples.all():
            additional_metadata_keys.update(sample.additional_metadata.keys())
            diagnoses.add(sample.diagnosis)
            disease_timings.add(sample.disease_timing)
            sample_seq_units = sample.seq_units.split(", ")
            sample_technologies = sample.technologies.split(", ")
            seq_units = seq_units.union(sample_seq_units)
            technologies = technologies.union(sample_technologies)

            if sample.has_cite_seq_data:
                modalities.add("CITE-seq")

            if sample.has_spatial_data:
                modalities.add("Spatial Data")

            # TODO(arkid15r): replace with a counter.
            if sample.diagnosis in diagnoses_counts:
                diagnoses_counts[sample.diagnosis] += 1
            else:
                diagnoses_counts[sample.diagnosis] = 1

            for seq_unit in sample_seq_units:
                for technology in sample_technologies:
                    summary = (sample.diagnosis, seq_unit.strip(), technology.strip())
                    if summary in summaries:
                        summaries[summary] += 1
                    else:
                        summaries[summary] = 1

        diagnoses_strings = sorted(
            (f"{diagnosis} ({count})" for diagnosis, count in diagnoses_counts.items())
        )
        downloadable_sample_count = project.samples.filter(
            sample_computed_file__isnull=False
        ).count()
        seq_units = sorted((seq_unit for seq_unit in seq_units if seq_unit))
        technologies = sorted((technology for technology in technologies if technology))

        project.additional_metadata_keys = ", ".join(sorted(additional_metadata_keys))
        project.diagnoses = ", ".join(sorted(diagnoses))
        project.diagnoses_counts = ", ".join(diagnoses_strings)
        project.disease_timings = ", ".join(disease_timings)
        project.downloadable_sample_count = downloadable_sample_count
        project.modalities = ", ".join(sorted(modalities))
        project.sample_count = project.samples.count()
        project.seq_units = ", ".join(seq_units)
        project.technologies = ", ".join(technologies)
        project.save()

        for (diagnosis, seq_unit, technology), count in summaries.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=project, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count
            project_summary.save(update_fields=("sample_count",))
