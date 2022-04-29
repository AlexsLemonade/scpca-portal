import os

from django.contrib.postgres.fields import JSONField
from django.db import models

from scpca_portal import common


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

        sample = cls(
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
    def get_output_single_cell_metadata_file_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_libraries_metadata.tsv")

    @staticmethod
    def get_output_spatial_metadata_file_path(scpca_sample_id):
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
    def output_single_cell_metadata_file_path(self):
        return Sample.get_output_single_cell_metadata_file_path(self.scpca_id)

    @property
    def output_spatial_data_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_data_file_path(self):
        return os.path.join(common.OUTPUT_DATA_DIR, self.output_spatial_data_file_name)

    @property
    def output_spatial_metadata_file_path(self):
        return Sample.get_output_spatial_metadata_file_path(self.scpca_id)
