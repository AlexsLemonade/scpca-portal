import subprocess
from pathlib import Path
from zipfile import ZipFile

from django.conf import settings
from django.db import models

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class ComputedFile(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    class MetadataFilenames:
        SINGLE_CELL_METADATA_FILE_NAME = "single_cell_metadata.tsv"
        SPATIAL_METADATA_FILE_NAME = "spatial_metadata.tsv"

    # TODO(ark): these values are redundant and need to be refactored in order not to violate DRY.
    class OutputFileModalities:
        MULTIPLEXED = "MULTIPLEXED"
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (MULTIPLEXED, "Multiplexed"),
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    class OutputFileTypes:
        PROJECT_MULTIPLEXED_ZIP = "PROJECT_MULTIPLEXED_ZIP"
        PROJECT_SPATIAL_ZIP = "PROJECT_SPATIAL_ZIP"
        PROJECT_ZIP = "PROJECT_ZIP"

        SAMPLE_MULTIPLEXED_ZIP = "SAMPLE_MULTIPLEXED_ZIP"
        SAMPLE_SPATIAL_ZIP = "SAMPLE_SPATIAL_ZIP"
        SAMPLE_ZIP = "SAMPLE_ZIP"

        CHOICES = (
            (PROJECT_MULTIPLEXED_ZIP, "Project Multiplexed ZIP"),
            (PROJECT_SPATIAL_ZIP, "Project Spatial ZIP"),
            (PROJECT_ZIP, "Project ZIP"),
            (SAMPLE_MULTIPLEXED_ZIP, "Sample Multiplexed ZIP"),
            (SAMPLE_SPATIAL_ZIP, "Sample Spatial ZIP"),
            (SAMPLE_ZIP, "Sample ZIP"),
        )

    class OutputFileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        )

    OUTPUT_README_FILE_NAME = "README.md"

    README_ANNDATA_FILE_NAME = "readme_anndata.md"
    README_ANNDATA_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_FILE_NAME

    README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
    README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

    README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
    README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

    README_SPATIAL_FILE_NAME = "readme_spatial.md"
    README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

    README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
    README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
    README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
    README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
    README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"

    format = models.TextField(choices=OutputFileFormats.CHOICES)
    modality = models.TextField(choices=OutputFileModalities.CHOICES)
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    type = models.TextField(choices=OutputFileTypes.CHOICES)
    workflow_version = models.TextField()

    project = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, related_name="project_computed_files"
    )
    sample = models.ForeignKey(
        "Sample", null=True, on_delete=models.CASCADE, related_name="sample_computed_files"
    )

    def __str__(self):
        return (
            f"'{self.project or self.sample}' {dict(self.OutputFileFormats.CHOICES)[self.format]} "
            f"computed file ({self.size_in_bytes}B)"
        )

    @classmethod
    def get_project_multiplexed_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined multiplexed data."""

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.MULTIPLEXED,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=project.output_multiplexed_computed_file_name,
            type=cls.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_MULTIPLEXED_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                project.output_multiplexed_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                for file_path in file_paths:
                    # Nest these under their sample id.
                    zip_file.write(file_path, Path(sample_id, file_path.name))

            if project.has_bulk_rna_seq:
                zip_file.write(project.input_bulk_metadata_file_path, "bulk_metadata.tsv")
                zip_file.write(project.input_bulk_quant_file_path, "bulk_quant.tsv")

        computed_file.has_bulk_rna_seq = project.has_bulk_rna_seq
        computed_file.has_cite_seq_data = project.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    @classmethod
    def get_project_single_cell_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined single cell data."""

        if file_format == cls.OutputFileFormats.ANN_DATA:
            computed_file_name = project.output_single_cell_anndata_computed_file_name
            readme_file_path = ComputedFile.README_ANNDATA_FILE_PATH
        else:
            computed_file_name = project.output_single_cell_computed_file_name
            readme_file_path = ComputedFile.README_SINGLE_CELL_FILE_PATH

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=computed_file_name,
            type=cls.OutputFileTypes.PROJECT_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(readme_file_path, ComputedFile.OUTPUT_README_FILE_NAME)
            zip_file.write(
                project.output_single_cell_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                for file_path in file_paths:
                    # Nest these under their sample id.
                    zip_file.write(file_path, Path(sample_id, file_path.name))

            if project.has_bulk_rna_seq:
                zip_file.write(project.input_bulk_metadata_file_path, "bulk_metadata.tsv")
                zip_file.write(project.input_bulk_quant_file_path, "bulk_quant.tsv")

        computed_file.has_bulk_rna_seq = project.has_bulk_rna_seq
        computed_file.has_cite_seq_data = project.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    @classmethod
    def get_project_spatial_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined spatial data."""

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SPATIAL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=project.output_spatial_computed_file_name,
            type=cls.OutputFileTypes.PROJECT_SPATIAL_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SPATIAL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                project.output_spatial_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                sample_path = project.get_sample_input_data_dir(sample_id)
                for file_path in file_paths:
                    zip_file.write(file_path, Path(file_path).relative_to(sample_path))

        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    @classmethod
    def get_sample_multiplexed_file(
        cls, sample, libraries, library_path_mapping, workflow_versions, file_format
    ):
        """
        Prepares a ready for saving single data file of sample's combined multiplexed data.
        Returns the data file and file mapping for a sample.
        """
        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.MULTIPLEXED,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=sample.output_multiplexed_computed_file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_MULTIPLEXED_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_name_path_mapping = {}
        for library in libraries:
            library_id = library["scpca_library_id"]
            for file_suffix in ("_filtered.rds", "_processed.rds", "_qc.html", "_unfiltered.rds"):
                file_name = f"{library_id}{file_suffix}"
                file_name_path_mapping[file_name] = Path(
                    library_path_mapping[library_id], file_name
                )

        if not computed_file.zip_file_path.exists():
            with ZipFile(computed_file.zip_file_path, "w") as zip_file:
                zip_file.write(
                    ComputedFile.README_MULTIPLEXED_FILE_PATH,
                    ComputedFile.OUTPUT_README_FILE_NAME,
                )
                zip_file.write(
                    sample.output_multiplexed_metadata_file_path,
                    ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME,
                )
                for file_name, file_path in file_name_path_mapping.items():
                    zip_file.write(file_path, file_name)

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = sample.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {"_".join(sample.multiplexed_ids): file_name_path_mapping.values()}

    @classmethod
    def get_sample_single_cell_file(cls, sample, libraries, workflow_versions, file_format):
        """
        Prepares a ready for saving single data file of sample's combined single cell data.
        Returns the data file and file mapping for a sample.
        """
        is_anndata_file_format = file_format == cls.OutputFileFormats.ANN_DATA
        if is_anndata_file_format:
            file_name = sample.output_single_cell_anndata_computed_file_name
            common_file_suffixes = (
                "filtered_rna.hdf5",
                "processed_rna.hdf5",
                "qc.html",
                "unfiltered_rna.hdf5",
            )
        else:
            file_name = sample.output_single_cell_computed_file_name
            common_file_suffixes = (
                "filtered.rds",
                "processed.rds",
                "qc.html",
                "unfiltered.rds",
            )
        cite_seq_anndata_file_suffixes = (
            "filtered_adt.hdf5",
            "processed_adt.hdf5",
            "unfiltered_adt.hdf5",
        )

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SINGLE_CELL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                sample.output_single_cell_metadata_file_path,
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME,
            )

            for library in libraries:
                file_suffixes = (
                    common_file_suffixes + cite_seq_anndata_file_suffixes
                    if is_anndata_file_format and library.get("has_citeseq")
                    else common_file_suffixes
                )
                for file_suffix in file_suffixes:
                    file_name = f"{library['scpca_library_id']}_{file_suffix}"
                    file_path = (
                        sample.project.get_sample_input_data_dir(sample.scpca_id) / file_name
                    )
                    file_paths.append(file_path)
                    zip_file.write(file_path, file_name)

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = sample.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {sample.scpca_id: file_paths}

    @classmethod
    def get_sample_spatial_file(cls, sample, libraries, workflow_versions, file_format):
        """
        Prepares a ready for saving single data file of sample's combined spatial data.
        Returns the data file and file mapping for a sample.
        """
        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SPATIAL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=sample.output_spatial_computed_file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_SPATIAL_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SPATIAL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                sample.output_spatial_metadata_file_path,
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME,
            )

            for library in libraries:
                library_path = Path(
                    sample.project.get_sample_input_data_dir(sample.scpca_id),
                    f"{library['scpca_library_id']}_spatial",
                )
                for item in library_path.rglob("*"):  # Add the entire directory contents.
                    zip_file.write(item, item.relative_to(library_path.parent))
                    file_paths.append(f"{Path(library_path, item.relative_to(library_path))}")

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = False  # Spatial downloads can't contain CITE-seq data.
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {sample.scpca_id: file_paths}

    @property
    def download_url(self):
        """A temporary URL from which the file can be downloaded."""
        return self.create_download_url()

    @property
    def is_project_multiplexed_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP

    @property
    def is_project_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_ZIP

    @property
    def is_project_spatial_zip(self):
        return self.type == ComputedFile.OutputFileTypes.PROJECT_SPATIAL_ZIP

    @property
    def metadata_file_name(self):
        if self.is_project_multiplexed_zip or self.is_project_zip:
            return ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
        if self.is_project_spatial_zip:
            return ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME

    @property
    def zip_file_path(self):
        return common.OUTPUT_DATA_PATH / self.s3_key

    def create_download_url(self):
        """Creates a temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            # Append the download date to the filename on download.
            date = utils.get_today_string()
            s3_key = Path(self.s3_key)

            return s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.s3_bucket,
                    "Key": self.s3_key,
                    "ResponseContentDisposition": (
                        f"attachment; filename = {s3_key.stem}_{date}{s3_key.suffix}"
                    ),
                },
                ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
            )

    def create_s3_file(self):
        """Uploads the computed file to S3 using AWS CLI tool."""
        subprocess.check_call(
            (
                "aws",
                "s3",
                "cp",
                str(self.zip_file_path),
                f"s3://{settings.AWS_S3_BUCKET_NAME}/{self.s3_key}",
            )
        )

    def delete_s3_file(self, force=False):
        # If we're not running in the cloud then we shouldn't try to
        # delete something from S3 unless force is set.
        if not settings.UPDATE_S3_DATA and not force:
            return False

        try:
            s3.delete_object(Bucket=self.s3_bucket, Key=self.s3_key)
        except Exception:
            logger.exception(
                "Failed to delete S3 object for Computed File.",
                computed_file=self.id,
                s3_object=self.s3_key,
            )
            return False

        return True
