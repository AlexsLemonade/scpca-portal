from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template.defaultfilters import pluralize

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile

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

    def __str__(self):
        return f"Sample {self.scpca_id} of {self.project}"

    @classmethod
    def get_from_dict(cls, data, project):
        """Prepares ready for saving sample object."""

        # If any project metadata exists in provided data dict, remove it
        if any(key in data for key in ["scpca_project_id", "project_title", "pi_name"]):
            data.pop("scpca_project_id", None)
            data.pop("project_title", None)
            data.pop("pi_name", None)

        sample = cls(
            age_at_diagnosis=data["age_at_diagnosis"],
            demux_cell_count_estimate=(data.get("demux_cell_count_estimate", None)),
            diagnosis=data["diagnosis"],
            disease_timing=data["disease_timing"],
            has_bulk_rna_seq=data.get("has_bulk_rna_seq", False),
            has_cite_seq_data=data.get("has_cite_seq_data", False),
            has_multiplexed_data=data.get("has_multiplexed_data", False),
            has_single_cell_data=data.get("has_single_cell_data", False),
            has_spatial_data=data.get("has_spatial_data", False),
            includes_anndata=data.get("includes_anndata", False),
            is_cell_line=utils.boolean_from_string(data.get("is_cell_line", False)),
            is_xenograft=utils.boolean_from_string(data.get("is_xenograft", False)),
            multiplexed_with=data.get("multiplexed_with"),
            sample_cell_count_estimate=(
                data.get("sample_cell_count_estimate")
                if not data.get("has_multiplexed_data", False)
                else None
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

    @classmethod
    def bulk_create_from_dicts(
        cls, samples_metadata: List[Dict], project, sample_id: str = None
    ) -> None:
        """Creates a list of sample objects from sample metadata libraries and then saves them."""
        samples = []
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if sample_id and scpca_sample_id != sample_id:
                continue

            samples.append(Sample.get_from_dict(sample_metadata, project))

        Sample.objects.bulk_create(samples)

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

    @staticmethod
    def create_sample_computed_files(
        combined_metadata,
        project,
        non_downloadable_sample_ids,
        multiplexed_library_path_mapping,
        max_workers=8,  # 8 = 2 file formats * 4 mappings.
        clean_up_output_data=True,
        update_s3=False,
        sample_id=None,
    ):
        """
        Generate computed files for each file format & modality within a given project's sample set.
        Populate file mappings for each sample's computed files,
        to be used when later generating the project zip.
        """

        # Organize zipfile locations by file format, then by modality
        # This data structure is needed to build the project zip in create_project_computed_files
        file_mappings_by_format = {
            ComputedFile.OutputFileFormats.ANN_DATA: {Sample.Modalities.SINGLE_CELL: {}},
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {
                Sample.Modalities.SINGLE_CELL: {},
                Sample.Modalities.SPATIAL: {},
                Sample.Modalities.MULTIPLEXED: {},
            },
        }

        workflow_versions_by_modality = {
            Sample.Modalities.SINGLE_CELL: set(),
            Sample.Modalities.SPATIAL: set(),
            Sample.Modalities.MULTIPLEXED: set(),
        }

        def create_sample_computed_file(future):
            computed_file, sample_to_files_mapping = future.result()
            if computed_file:
                computed_file.process_computed_file(clean_up_output_data, update_s3)

            modality = (
                computed_file.modality
                if not computed_file.sample.has_multiplexed_data
                else Sample.Modalities.MULTIPLEXED
            )
            file_format = computed_file.format
            file_mappings_by_format[file_format][modality].update(sample_to_files_mapping)

        samples = (
            Sample.objects.filter(project__scpca_id=project.scpca_id)
            if sample_id is None
            else Sample.objects.filter(scpca_id=sample_id)
        )
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
            for sample in samples:
                # Skip computed files creation if sample directory does not exist.
                if sample.scpca_id not in non_downloadable_sample_ids:
                    libraries = [
                        library
                        for library in combined_metadata[Sample.Modalities.SINGLE_CELL]
                        if library["scpca_sample_id"] == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    workflow_versions_by_modality[Sample.Modalities.SINGLE_CELL].update(
                        workflow_versions
                    )

                    for file_format in sample.single_cell_file_formats:
                        tasks.submit(
                            ComputedFile.get_sample_single_cell_file,
                            sample,
                            libraries,
                            workflow_versions,
                            file_format,
                        ).add_done_callback(create_sample_computed_file)

                    if sample.has_spatial_data:
                        libraries = [
                            library
                            for library in combined_metadata[Sample.Modalities.SPATIAL]
                            if library["scpca_sample_id"] == sample.scpca_id
                        ]
                        workflow_versions = [library["workflow_version"] for library in libraries]
                        workflow_versions_by_modality[Sample.Modalities.SPATIAL].update(
                            workflow_versions
                        )
                        tasks.submit(
                            ComputedFile.get_sample_spatial_file,
                            sample,
                            libraries,
                            workflow_versions,
                            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                        ).add_done_callback(create_sample_computed_file)

                if sample.has_multiplexed_data:
                    libraries = [
                        library
                        for library in combined_metadata[Sample.Modalities.MULTIPLEXED]
                        if library.get("scpca_sample_id") == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    workflow_versions_by_modality[Sample.Modalities.MULTIPLEXED].update(
                        workflow_versions
                    )

                    # Get the lock for current sample.
                    sample_lock = locks["_".join(sample.multiplexed_ids)]

                    tasks.submit(
                        ComputedFile.get_sample_multiplexed_file,
                        sample,
                        libraries,
                        multiplexed_library_path_mapping,
                        workflow_versions,
                        ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                        lock=sample_lock,
                    ).add_done_callback(create_sample_computed_file)

        return (file_mappings_by_format, workflow_versions_by_modality)
