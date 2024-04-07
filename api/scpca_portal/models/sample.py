from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common, utils
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile


class Sample(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    class Modalities:
        BULK_RNA_SEQ = "BULK_RNA_SEQ"
        CITE_SEQ = "CITE_SEQ"
        MULTIPLEXED = "MULTIPLEXED"
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        NAME_MAPPING = {
            BULK_RNA_SEQ: "Bulk RNA-seq",
            CITE_SEQ: "CITE-seq",
            MULTIPLEXED: "Multiplexed",
            SPATIAL: "Spatial Data",
        }

    additional_metadata = models.JSONField(default=dict)
    age_at_diagnosis = models.TextField(blank=True, null=True)
    demux_cell_count_estimate = models.IntegerField(null=True)
    diagnosis = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_multiplexed_data = models.BooleanField(default=False)
    has_single_cell_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    includes_anndata = models.BooleanField(default=False)
    is_cell_line = models.BooleanField(default=False)
    is_xenograft = models.BooleanField(default=False)
    multiplexed_with = ArrayField(models.TextField(), default=list)
    sample_cell_count_estimate = models.IntegerField(null=True)
    scpca_id = models.TextField(unique=True)
    seq_units = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    subdiagnosis = models.TextField(blank=True, null=True)
    technologies = models.TextField()
    tissue_location = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="samples")

    def __str__(self):
        return f"Sample {self.scpca_id} of {self.project}"

    @classmethod
    def get_from_dict(cls, data, project):
        """Prepares ready for saving sample object."""

        has_multiplexed_data = bool(data.get("multiplexed_with"))
        sample = cls(
            age_at_diagnosis=data["age_at_diagnosis"],
            demux_cell_count_estimate=(
                data.get("demux_cell_count_estimate") if has_multiplexed_data else None
            ),
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            has_bulk_rna_seq=data.get("has_bulk_rna_seq", False),
            has_cite_seq_data=data.get("has_cite_seq_data", False),
            has_multiplexed_data=has_multiplexed_data,
            has_single_cell_data=data.get("has_single_cell_data", False),
            has_spatial_data=data.get("has_spatial_data", False),
            includes_anndata=data.get("includes_anndata", False),
            is_cell_line=utils.boolean_from_string(data.get("is_cell_line", False)),
            is_xenograft=utils.boolean_from_string(data.get("is_xenograft", False)),
            multiplexed_with=data.get("multiplexed_with"),
            sample_cell_count_estimate=(
                data.get("sample_cell_count_estimate") if not has_multiplexed_data else None
            ),
            project=project,
            scpca_id=data.pop("scpca_sample_id"),
            seq_units=data.get("seq_units", ""),
            sex=data["sex"],
            subdiagnosis=data["subdiagnosis"],
            technologies=data.get("technologies", ""),
            tissue_location=data["tissue_location"],
            treatment=data.get("treatment", ""),
        )

        # Additional metadata varies project by project.
        # Generally, whatever's not on the Sample model is additional.
        sample.additional_metadata = {
            key: value for key, value in data.items() if not hasattr(sample, key)
        }

        return sample

    @staticmethod
    def get_output_metadata_file_path(scpca_sample_id, modality):
        return {
            Sample.Modalities.MULTIPLEXED: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_multiplexed_metadata.tsv",
            Sample.Modalities.SINGLE_CELL: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_libraries_metadata.tsv",
            Sample.Modalities.SPATIAL: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_spatial_metadata.tsv",
        }.get(modality)

    @property
    def modalities(self):
        attr_name_modality_mapping = {
            "has_bulk_rna_seq": Sample.Modalities.BULK_RNA_SEQ,
            "has_cite_seq_data": Sample.Modalities.CITE_SEQ,
            "has_multiplexed_data": Sample.Modalities.MULTIPLEXED,
            "has_spatial_data": Sample.Modalities.SPATIAL,
        }

        return sorted(
            [
                Sample.Modalities.NAME_MAPPING[modality_name]
                for attr_name, modality_name in attr_name_modality_mapping.items()
                if getattr(self, attr_name)
            ]
        )

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
        return Sample.get_output_metadata_file_path(self.scpca_id, Sample.Modalities.MULTIPLEXED)

    @property
    def output_single_cell_computed_file_name(self):
        return f"{self.scpca_id}.zip"

    @property
    def output_single_cell_anndata_computed_file_name(self):
        return f"{self.scpca_id}_anndata.zip"

    @property
    def output_single_cell_metadata_file_path(self):
        return Sample.get_output_metadata_file_path(self.scpca_id, Sample.Modalities.SINGLE_CELL)

    @property
    def output_spatial_computed_file_name(self):
        return f"{self.scpca_id}_spatial.zip"

    @property
    def output_spatial_metadata_file_path(self):
        return Sample.get_output_metadata_file_path(self.scpca_id, Sample.Modalities.SPATIAL)

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
            return self.sample_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                type=ComputedFile.OutputFileTypes.SAMPLE_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_computed_file(self):
        try:
            return self.sample_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                type=ComputedFile.OutputFileTypes.SAMPLE_ZIP,
            )
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

    @property
    def single_cell_file_formats(self):
        file_formats = []
        if self.has_single_cell_data:
            file_formats.append(ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT)
        if self.includes_anndata:
            file_formats.append(ComputedFile.OutputFileFormats.ANN_DATA)
        return file_formats
