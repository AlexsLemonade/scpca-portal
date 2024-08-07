from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.template.defaultfilters import pluralize

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.library import Library

logger = get_and_configure_logger(__name__)


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
    libraries = models.ManyToManyField(Library, related_name="samples")

    def __str__(self):
        return f"Sample {self.scpca_id} of {self.project}"

    @classmethod
    def get_from_dict(cls, data, project):
        """Prepares ready for saving sample object."""
        sample = cls(
            age_at_diagnosis=data["age_at_diagnosis"],
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            is_cell_line=utils.boolean_from_string(data.get("is_cell_line", False)),
            is_xenograft=utils.boolean_from_string(data.get("is_xenograft", False)),
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

        # Additional metadata varies project by project.
        # Generally, whatever's not on the Sample model is additional.
        sample.additional_metadata = {
            key: value
            for key, value in data.items()
            if not hasattr(sample, key)
            # Don't include project metadata keys (needed for writing)
            and key not in ("scpca_project_id", "project_title", "pi_name", "submitter")
            # Exclude deliberate model attribute and file field name mismatch
            and key != "scpca_sample_id"
        }

        return sample

    @classmethod
    def bulk_create_from_dicts(cls, samples_metadata: List[Dict], project) -> None:
        """Creates a list of sample objects from sample metadata libraries and then saves them."""
        samples = []
        for sample_metadata in samples_metadata:
            samples.append(Sample.get_from_dict(sample_metadata, project))

        Sample.objects.bulk_create(samples)

    def get_metadata(self) -> Dict:
        sample_metadata = {
            "scpca_sample_id": self.scpca_id,
        }

        included_sample_attributes = {
            "age_at_diagnosis",
            "demux_cell_count_estimate",
            "diagnosis",
            "disease_timing",
            "sex",
            "subdiagnosis",
            "tissue_location",
            "includes_anndata",
            "is_cell_line",
            "is_xenograft",
            "sample_cell_count_estimate",
        }

        sample_metadata.update({key: getattr(self, key) for key in included_sample_attributes})
        # Update name from attribute name to expected output name
        sample_metadata["sample_cell_estimate"] = sample_metadata.pop("demux_cell_count_estimate")

        sample_metadata.update(
            {key: self.additional_metadata[key] for key in self.additional_metadata}
        )

        return sample_metadata

    def get_config_identifier(self, download_config: Dict) -> str:
        """
        Returns a unique identifier for the sample and download config combination.
        Multiplexed samples are not considered unique as they share the same output.
        """
        return "_".join(self.multiplexed_ids + sorted(download_config.values()))

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

    def get_download_config_file_output_name(self, download_config: Dict) -> str:
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

        return f"{'_'.join(name_segments)}.zip"

    @staticmethod
    def create_computed_files(
        project,
        max_workers=8,  # 8 = 2 file formats * 4 mappings.
        clean_up_output_data=True,
        update_s3=False,
    ):
        """Prepares ready for saving project computed files based on generated file mappings."""

        def on_get_sample_file(future):
            if computed_file := future.result():

                # Only upload and clean up the last if multiplexed
                if computed_file.sample.is_last_multiplexed_sample:
                    if update_s3:
                        computed_file.upload_s3_file()
                    if clean_up_output_data:
                        computed_file.clean_up_local_computed_file()
                computed_file.save()

            # Close DB connection for each thread.
            connection.close()

        samples = Sample.objects.filter(project__scpca_id=project.scpca_id)
        logger.info(
            f"Processing {len(samples)} sample{pluralize(len(samples))} using "
            f"{max_workers} worker{pluralize(max_workers)}"
        )

        # Prepare a threading.Lock for each sample, with the chief purpose being to protect
        # multiplexed samples that shares a zip file.
        locks = {}
        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for sample in samples:
                for config in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGURATIONS:
                    sample_lock = locks.setdefault(sample.get_config_identifier(config), Lock())
                    tasks.submit(
                        ComputedFile.get_sample_file,
                        sample,
                        config,
                        sample.get_download_config_file_output_name(config),
                        sample_lock,
                    ).add_done_callback(on_get_sample_file)
