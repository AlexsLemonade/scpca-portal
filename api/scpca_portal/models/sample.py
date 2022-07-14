import os

from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile


class Sample(TimestampedModel):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    additional_metadata = models.JSONField(default=dict)
    age_at_diagnosis = models.TextField(blank=True, null=True)
    demux_cell_count_estimate = models.IntegerField(null=True)
    diagnosis = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_bulk_rna_seq = models.BooleanField(default=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_multiplexed_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    multiplexed_with = ArrayField(models.TextField(), default=list)
    sample_cell_count_estimate = models.IntegerField(null=True)
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
            "demux_cell_count_estimate",
            "diagnosis",
            "disease_timing",
            "sample_cell_count_estimate",
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
        has_multiplexed_data = bool(data.get("multiplexed_with"))

        sample = cls(
            additional_metadata=additional_metadata,
            age_at_diagnosis=data["age"],
            demux_cell_count_estimate=(
                data.get("demux_cell_count_estimate") if has_multiplexed_data else None
            ),
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            has_bulk_rna_seq=data.get("has_bulk_rna_seq", False),
            has_cite_seq_data=data.get("has_cite_seq_data", False),
            has_multiplexed_data=has_multiplexed_data,
            has_spatial_data=data.get("has_spatial_data", False),
            multiplexed_with=data.get("multiplexed_with"),
            sample_cell_count_estimate=(
                data.get("sample_cell_count_estimate") if not has_multiplexed_data else None
            ),
            project=project,
            scpca_id=data["scpca_sample_id"],
            seq_units=data.get("seq_units", ""),
            sex=data["sex"],
            subdiagnosis=data["subdiagnosis"],
            technologies=data.get("technologies", ""),
            tissue_location=data["tissue_location"],
            treatment=data.get("treatment", ""),
        )
        sample.save()

        return sample

    @staticmethod
    def get_output_multiplexed_metadata_file_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_multiplexed_metadata.tsv")

    @staticmethod
    def get_output_single_cell_metadata_file_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_libraries_metadata.tsv")

    @staticmethod
    def get_output_spatial_metadata_file_path(scpca_sample_id):
        return os.path.join(common.OUTPUT_DATA_DIR, f"{scpca_sample_id}_spatial_metadata.tsv")

    @property
    def modalities(self):
        modalities = []

        if self.has_bulk_rna_seq:
            modalities.append("Bulk")

        if self.has_cite_seq_data:
            modalities.append("CITE-seq")

        if self.has_multiplexed_data:
            modalities.append("Multiplexed")

        if self.has_spatial_data:
            modalities.append("Spatial Transcriptomics")

        if modalities:
            return ", ".join(modalities)

    @property
    def computed_files(self):
        return self.sample_computed_files.order_by("created_at")

    @property
    def multiplexed_ids(self):
        multiplexed_sample_ids = [self.scpca_id]
        multiplexed_sample_ids.extend(self.multiplexed_with)

        return sorted(multiplexed_sample_ids)

    @property
    def output_multiplexed_computed_file_name(self):
        return f"{'_'.join(self.multiplexed_ids)}_multiplexed.zip"

    @property
    def output_multiplexed_metadata_file_path(self):
        return Sample.get_output_multiplexed_metadata_file_path(self.scpca_id)

    @property
    def output_single_cell_computed_file_name(self):
        return f"{self.scpca_id}.zip"

    @property
    def output_single_cell_metadata_file_path(self):
        return Sample.get_output_single_cell_metadata_file_path(self.scpca_id)

    @property
    def output_spatial_computed_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_metadata_file_path(self):
        return Sample.get_output_spatial_metadata_file_path(self.scpca_id)

    @property
    def multiplexed_computed_file(self):
        try:
            return self.sample_computed_files.get(
                type=ComputedFile.OutputFileTypes.SAMPLE_MULTIPLEXED_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_computed_file(self):
        try:
            return self.sample_computed_files.get(type=ComputedFile.OutputFileTypes.SAMPLE_ZIP)
        except ComputedFile.DoesNotExist:
            pass

    @property
    def spatial_computed_file(self):
        try:
            return self.sample_computed_files.get(
                type=ComputedFile.OutputFileTypes.SAMPLE_SPATIAL_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass
