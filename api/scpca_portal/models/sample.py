import os
from pathlib import Path
from typing import Dict, List
from zipfile import ZipFile

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from scpca_portal import common
from scpca_portal.models.computed_file import ComputedFile


class Sample(models.Model):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    additional_metadata = JSONField(default=dict)
    age_at_diagnosis = models.TextField(blank=True, null=True)
    cell_count = models.IntegerField()
    diagnosis = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_cite_seq_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    scpca_id = models.TextField(unique=True, null=False)
    seq_units = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    subdiagnosis = models.TextField(blank=True, null=True)
    technologies = models.TextField(null=False)
    tissue_location = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)

    project = models.ForeignKey(
        "Project", null=False, on_delete=models.CASCADE, related_name="samples"
    )

    def __str__(self):
        return f"Sample {self.scpca_id} of {self.project}"

    @classmethod
    def create_from_dict(cls, data, project):
        # First figure out what metadata is additional. This varies project by
        # project, so whatever's not on the Sample model is additional.
        sample_columns = (
            "age",
            "cell_count",
            "diagnosis",
            "disease_timing",
            "scpca_library_id",  # Also include this because we don't want it in additional_metadata.
            "scpca_sample_id",
            "seq_units",
            "sex",
            "subdiagnosis",
            "technologies",
            "tissue_location",
            "treatment",
        )
        additional_metadata = {k: v for k, v in data.items() if k not in sample_columns}

        sample = Sample(
            additional_metadata=additional_metadata,
            age_at_diagnosis=data["age"],
            cell_count=data["cell_count"],
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            project=project,
            scpca_id=data["scpca_sample_id"],
            seq_units=data.get("seq_units", ""),
            sex=data["sex"],
            subdiagnosis=data["subdiagnosis"],
            technologies=data.get("technologies", ""),
            tissue_location=data["tissue_location"],
            treatment=data.get("treatment"),
        )
        sample.save()

        return sample

    @staticmethod
    def get_output_metadata_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_libraries_metadata.tsv")

    @staticmethod
    def get_output_spatial_metadata_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_spatial_metadata.tsv")

    # TODO(arkid15r): remove the property after BE/FE refactoring.
    @property
    def computed_file(self):
        return self.sample_computed_file.first()

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

    def create_single_cell_data_file(self, libraries_metadata: List[Dict], workflow_version: str):
        libraries = [lm for lm in libraries_metadata if lm["scpca_sample_id"] == self.scpca_id]

        computed_file = ComputedFile(
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=self.output_single_cell_data_file_name,
            smpl=self,
            type=ComputedFile.FileTypes.SAMPLE_ZIP,
            workflow_version=workflow_version,
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(ComputedFile.README_FILE_PATH, ComputedFile.README_FILE_NAME)
            zip_file.write(
                Sample.get_output_metadata_path(self.scpca_id),
                ComputedFile.FileNames.SINGLE_CELL_METADATA_FILE_NAME,
            )

            file_paths = []
            for library in libraries:
                for file_postfix in ("_filtered.rds", "_qc.html", "_unfiltered.rds"):
                    file_name = f"{library['scpca_library_id']}{file_postfix}"
                    file_path = os.path.join(
                        self.project.get_sample_input_data_dir(self.scpca_id), file_name
                    )
                    file_paths.append(file_path)
                    zip_file.write(file_path, file_name)

        computed_file.size_in_bytes = os.path.getsize(computed_file.zip_file_path)
        computed_file.save()

        return computed_file, {self.scpca_id: file_paths}

    def create_spatial_data_file(
        self, libraries_metadata: List[Dict], workflow_version: str,
    ):

        computed_file = ComputedFile(
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=self.output_spatial_data_file_name,
            smpl=self,
            type=ComputedFile.FileTypes.SAMPLE_SPATIAL_ZIP,
            workflow_version=workflow_version,
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_object:
            zip_object.write(ComputedFile.README_FILE_PATH, ComputedFile.README_FILE_NAME)
            zip_object.write(
                Sample.get_output_spatial_metadata_path(self.scpca_id),
                ComputedFile.FileNames.SPATIAL_METADATA_FILE_NAME,
            )

            libraries = [lm for lm in libraries_metadata if lm["scpca_sample_id"] == self.scpca_id]
            for library in libraries:
                library_path = Path(
                    os.path.join(
                        self.project.get_sample_input_data_dir(self.scpca_id),
                        f"{library['scpca_library_id']}_spatial",
                    )
                )
                for item in library_path.rglob("*"):  # Add the entire directory contents.
                    zip_object.write(item, item.relative_to(library_path.parent))
                    file_paths.append(f"{Path(library_path, item.relative_to(library_path))}")

        computed_file.size_in_bytes = os.path.getsize(computed_file.zip_file_path)
        computed_file.save()

        return computed_file, {self.scpca_id: file_paths}
