from typing import Dict, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import Modalities
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.library import Library

logger = get_and_configure_logger(__name__)


class Sample(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    MODALITY_NAME_MAPPING = {
        Modalities.BULK_RNA_SEQ: "Bulk RNA-seq",
        Modalities.CITE_SEQ: "CITE-seq",
        Modalities.MULTIPLEXED: "Multiplexed",
        Modalities.SINGLE_CELL: "Single Cell",
        Modalities.SPATIAL: "Spatial Data",
    }

    class ModalitiesNameMapping:
        names = {
            Modalities.BULK_RNA_SEQ: "Bulk RNA-seq",
            Modalities.CITE_SEQ: "CITE-seq",
            Modalities.MULTIPLEXED: "Multiplexed",
            Modalities.SPATIAL: "Spatial Data",
        }

        @staticmethod
        def get_name(modality):
            return Sample.ModalitiesNameMapping.names.get(modality)

    age = models.TextField()
    age_timing = models.TextField()
    demux_cell_count_estimate_sum = models.IntegerField(null=True)
    diagnosis = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_multiplexed_data = models.BooleanField(default=False)
    has_single_cell_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    includes_anndata = models.BooleanField(default=False)
    is_cell_line = models.BooleanField(default=False)
    is_xenograft = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
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
    libraries = models.ManyToManyField(Library, related_name="samples")

    def __str__(self):
        return f"Sample {self.scpca_id} of {self.project}"

    @classmethod
    def get_from_dict(cls, data, project):
        """Prepares ready for saving sample object."""
        sample = cls(
            age=data["age"],
            age_timing=data["age_timing"],
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            is_cell_line=utils.boolean_from_string(data.get("is_cell_line", False)),
            is_xenograft=utils.boolean_from_string(data.get("is_xenograft", False)),
            metadata=data,
            multiplexed_with=data.get("multiplexed_with", []),
            sample_cell_count_estimate=(data.get("sample_cell_count_estimate", None)),
            project=project,
            scpca_id=data["scpca_sample_id"],
            seq_units=data.get("seq_units", ""),
            sex=data["sex"],
            subdiagnosis=data["subdiagnosis"],
            technologies=data.get("technologies", ""),
            tissue_location=data["tissue_location"],
            treatment=data.get("treatment", ""),
        )

        return sample

    @classmethod
    def bulk_create_from_dicts(cls, samples_metadata: List[Dict], project) -> None:
        """Creates a list of sample objects from sample metadata libraries and then saves them."""
        samples = []
        for sample_metadata in samples_metadata:
            samples.append(Sample.get_from_dict(sample_metadata, project))

        Sample.objects.bulk_create(samples)

    @property
    def additional_metadata(self):
        return {
            key: value
            for key, value in self.metadata.items()
            if not hasattr(self, key)
            # These fields are accounted for elsewhere,
            # either in different models or by different names
            and key not in ("scpca_sample_id", "scpca_project_id", "submitter")
        }

    @property
    def valid_download_config_names(self) -> List[str]:
        return [
            download_config_name
            for download_config_name, download_config in common.SAMPLE_DOWNLOAD_CONFIGS.items()
            if self.get_libraries(download_config).exists()
        ]

    @property
    def valid_download_configs(self) -> List[Dict]:
        return [
            download_config
            for download_config in common.SAMPLE_DOWNLOAD_CONFIGS.values()
            if self.get_libraries(download_config).exists()
        ]

    def get_metadata(self) -> Dict:
        excluded_metadata_attributes = {
            "scpca_project_id",
            "submitter",  # included in project metadata under the name pi_name
        }

        sample_metadata = {
            key: value
            for key, value in self.metadata.items()
            if key not in excluded_metadata_attributes
        }
        sample_metadata["includes_anndata"] = self.includes_anndata

        return sample_metadata

    def get_libraries(self, download_config: Dict = {}):  # -> QuerySet[Library]:
        """
        Return all of a sample's associated libraries filtered by the passed download config.
        """
        if not download_config:
            return self.libraries.all()

        if download_config not in common.SAMPLE_DOWNLOAD_CONFIGS.values():
            raise ValueError("Invalid download_config passed. Unable to retrieve libraries.")

        return self.libraries.filter(
            modality=download_config["modality"],
            formats__contains=[download_config["format"]],
        )

    def get_computed_file(self, download_config: Dict) -> ComputedFile:
        "Return the sample computed file that matches the passed download_config."
        return self.computed_files.filter(
            modality=download_config["modality"],
            format=download_config["format"],
        ).first()

    def get_config_identifier(self, download_config: Dict) -> str:
        """
        Returns a unique identifier for the sample and download config combination.
        Multiplexed samples are not considered unique as they share the same output.
        """
        return "_".join(self.multiplexed_ids + sorted(download_config.values()))

    @staticmethod
    def get_output_metadata_file_path(scpca_sample_id, modality):
        return {
            Modalities.MULTIPLEXED: settings.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_multiplexed_metadata.tsv",
            Modalities.SINGLE_CELL: settings.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_libraries_metadata.tsv",
            Modalities.SPATIAL: settings.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_spatial_metadata.tsv",
        }.get(modality)

    @property
    def modalities(self):
        attr_name_modality_mapping = {
            "has_bulk_rna_seq": Modalities.BULK_RNA_SEQ,
            "has_cite_seq_data": Modalities.CITE_SEQ,
            "has_multiplexed_data": Modalities.MULTIPLEXED,
            "has_spatial_data": Modalities.SPATIAL,
        }

        return sorted(
            [
                Sample.MODALITY_NAME_MAPPING[modality_name]
                for attr_name, modality_name in attr_name_modality_mapping.items()
                if getattr(self, attr_name)
            ]
        )

    @property
    def computed_files(self):
        return self.sample_computed_files.order_by("created_at")

    @property
    def multiplexed_with_samples(self):
        return (
            Sample.objects.filter(libraries__in=self.libraries.filter(is_multiplexed=True))
            .distinct()
            .exclude(scpca_id=self.scpca_id)
        )

    @property
    def multiplexed_ids(self):
        multiplexed_sample_ids = [self.scpca_id]
        multiplexed_sample_ids.extend(self.multiplexed_with)

        return sorted(multiplexed_sample_ids)

    @property
    def is_last_multiplexed_sample(self):
        """Return True if sample id is highest in list of multiplexed ids, False if not"""
        return self.scpca_id == self.multiplexed_ids[-1]

    @property
    def multiplexed_computed_file(self):
        try:
            return self.sample_computed_files.get(
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                has_multiplexed_data=True,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_computed_file(self):
        try:
            return self.sample_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                has_multiplexed_data=False,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def single_cell_anndata_computed_file(self):
        try:
            return self.sample_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL,
                has_multiplexed_data=False,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def spatial_computed_file(self):
        try:
            return self.sample_computed_files.get(
                modality=ComputedFile.OutputFileModalities.SPATIAL
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

    def get_output_file_name(self, download_config: Dict) -> str:
        """
        Accumulates all applicable name segments, concatenates them with an underscore delimiter,
        and returns the string as a unique zip file name.
        """
        name_segments = [
            "_".join(self.multiplexed_ids),
            download_config["modality"],
            download_config["format"],
        ]
        if self.has_multiplexed_data:
            name_segments.append("MULTIPLEXED")

        # Change to filename format must be accompanied by an entry in the docs.
        # Each segment should have hyphens and no underscores
        # Each segment should be joined by underscores
        file_name = "_".join([segment.replace("_", "-") for segment in name_segments])

        return f"{file_name}.zip"

    def purge(self) -> None:
        """Purges a sample and its associated libraries"""
        for library in self.libraries.all():
            # If library has other samples that it is related to, then don't delete it
            if library.samples.count() == 1:
                library.delete()
        self.delete()

    def purge_computed_files(self, delete_from_s3: bool = False) -> None:
        for computed_file in self.sample_computed_files.all():
            computed_file.purge(delete_from_s3)
