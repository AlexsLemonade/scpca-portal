import subprocess
from pathlib import Path
from threading import Lock
from zipfile import ZipFile

from django.conf import settings
from django.db import connection, models

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

    class OutputFileModalities:
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    class OutputFileSubModalities:
        MULTIPLEXED = "MULTIPLEXED"

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

    README_ANNDATA_MERGED_FILE_NAME = "readme_anndata_merged.md"
    README_ANNDATA_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_MERGED_FILE_NAME

    README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
    README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

    README_SINGLE_CELL_MERGED_FILE_NAME = "readme_single_cell_merged.md"
    README_SINGLE_CELL_MERGED_FILE_PATH = (
        common.OUTPUT_DATA_PATH / README_SINGLE_CELL_MERGED_FILE_NAME
    )

    README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
    README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

    README_SPATIAL_FILE_NAME = "readme_spatial.md"
    README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

    README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
    README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
    README_TEMPLATE_ANNDATA_MERGED_FILE_PATH = README_TEMPLATE_PATH / "anndata_merged.md"
    README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
    README_TEMPLATE_SINGLE_CELL_MERGED_FILE_PATH = README_TEMPLATE_PATH / "single_cell_merged.md"
    README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
    README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"

    format = models.TextField(choices=OutputFileFormats.CHOICES)
    includes_merged = models.BooleanField(default=False)
    modality = models.TextField(choices=OutputFileModalities.CHOICES)
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    workflow_version = models.TextField()
    includes_celltype_report = models.BooleanField(default=False)

    project = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, related_name="project_computed_files"
    )
    sample = models.ForeignKey(
        "Sample", null=True, on_delete=models.CASCADE, related_name="sample_computed_files"
    )

    def __str__(self):
        return (
            f"'{self.project or self.sample}' "
            f"{dict(self.OutputFileModalities.CHOICES)[self.modality]} "
            f"{dict(self.OutputFileFormats.CHOICES)[self.format]} "
            f"computed file ({self.size_in_bytes}B)"
        )

    @classmethod
    def get_project_merged_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's merged data."""

        project_file_mapping = {
            project.input_merged_summary_report_file_path: (
                f"{project.scpca_id}_merged-summary-report.html"
            ),
        }

        if file_format == cls.OutputFileFormats.ANN_DATA:
            if not project.includes_merged_anndata:
                return None
            computed_file_name = project.output_merged_anndata_computed_file_name
            readme_file_path = ComputedFile.README_ANNDATA_MERGED_FILE_PATH
            project_file_mapping[
                f"{project.input_merged_data_path}/{project.scpca_id}_merged_rna.h5ad"
            ] = f"{project.scpca_id}_merged_rna.h5ad"

            if project.has_cite_seq_data:
                project_file_mapping[
                    f"{project.input_merged_data_path}/{project.scpca_id}_merged_adt.h5ad"
                ] = f"{project.scpca_id}_merged_adt.h5ad"
        else:
            if not project.includes_merged_sce:
                return None
            computed_file_name = project.output_merged_computed_file_name
            readme_file_path = ComputedFile.README_SINGLE_CELL_MERGED_FILE_PATH

            project_file_mapping[
                f"{project.input_merged_data_path}/{project.scpca_id}_merged.rds"
            ] = f"{project.scpca_id}_merged.rds"

        computed_file = cls(
            format=file_format,
            includes_merged=True,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=computed_file_name,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        project_file_mapping[readme_file_path] = ComputedFile.OUTPUT_README_FILE_NAME
        project_file_mapping[
            project.output_single_cell_metadata_file_path
        ] = computed_file.metadata_file_name

        if project.has_bulk_rna_seq:
            project_file_mapping[project.input_bulk_metadata_file_path] = "bulk_metadata.tsv"
            project_file_mapping[project.input_bulk_quant_file_path] = "bulk_quant.tsv"

        sample_file_suffixes = {
            "celltype-report.html",
            "qc.html",
        }

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            for src, dst in project_file_mapping.items():
                zip_file.write(src, dst)

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                for file_path in file_paths:
                    if str(file_path).split("_")[-1] not in sample_file_suffixes:
                        continue
                    # Nest these under their sample id.
                    zip_file.write(file_path, Path("individual_reports", sample_id, file_path.name))

        computed_file.has_bulk_rna_seq = project.has_bulk_rna_seq
        computed_file.has_cite_seq_data = project.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    @classmethod
    def get_project_multiplexed_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined multiplexed data."""

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=project.output_multiplexed_computed_file_name,
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
        computed_file.has_multiplexed_data = project.has_multiplexed_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size
        computed_file.includes_celltype_report = project.samples.filter(is_cell_line=False).exists()

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
        cls, sample, libraries, library_path_mapping, workflow_versions, file_format, lock: Lock
    ):
        """
        Prepares a ready for saving single data file of sample's combined multiplexed data.
        Returns the data file and file mapping for a sample.
        """
        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=sample.output_multiplexed_computed_file_name,
            sample=sample,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        # cell lines do not have celltype reports
        includes_celltype_report = not sample.is_cell_line

        file_name_path_mapping = {}
        for library in libraries:
            library_id = library["scpca_library_id"]
            file_suffixes = ["filtered.rds", "processed.rds", "qc.html", "unfiltered.rds"]

            if includes_celltype_report:
                file_suffixes.append("celltype-report.html")

            # TEMP: Currently there are no celltype-reports for multiplexed samples.
            # TEMP: Part 1 of 2
            includes_celltype_report = False

            for file_suffix in file_suffixes:
                file_name = f"{library_id}_{file_suffix}"
                file_name_path_mapping[file_name] = Path(
                    library_path_mapping[library_id], file_name
                )

                # TEMP: Currently there are no celltype-reports for multiplexed samples.
                # TEMP: Part 2 of 2
                # This prevents us from trying to copy over a report that does not exist.
                # This is only here to prevent us from not catching an error of missing other files.
                if (
                    file_suffix == "celltype-report.html"
                    and not file_name_path_mapping[file_name].exists()
                ):
                    del file_name_path_mapping[file_name]
                else:
                    includes_celltype_report = True

        # This check does not function as expected when multiple threads
        # check before the compilation is complete. Here we use a lock that
        # is specific to all samples that share the same zip_file_path.
        with lock:
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
        computed_file.has_multiplexed_data = sample.has_multiplexed_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size
        computed_file.includes_celltype_report = includes_celltype_report

        return computed_file, {"_".join(sample.multiplexed_ids): file_name_path_mapping.values()}

    @classmethod
    def get_sample_single_cell_file(cls, sample, libraries, workflow_versions, file_format):
        """
        Prepares a ready for saving single data file of sample's combined single cell data.
        Returns the data file and file mapping for a sample.
        """
        is_anndata_file_format = file_format == cls.OutputFileFormats.ANN_DATA
        # cell lines do not have celltype reports
        includes_celltype_report = not sample.is_cell_line

        if is_anndata_file_format:
            file_name = sample.output_single_cell_anndata_computed_file_name
            readme_file_path = ComputedFile.README_ANNDATA_FILE_PATH
            common_file_suffixes = [
                "filtered_rna.h5ad",
                "processed_rna.h5ad",
                "qc.html",
                "unfiltered_rna.h5ad",
            ]
        else:
            file_name = sample.output_single_cell_computed_file_name
            readme_file_path = ComputedFile.README_SINGLE_CELL_FILE_PATH
            common_file_suffixes = [
                "filtered.rds",
                "processed.rds",
                "qc.html",
                "unfiltered.rds",
            ]

        if includes_celltype_report:
            common_file_suffixes.append("celltype-report.html")

        cite_seq_anndata_file_suffixes = [
            "filtered_adt.h5ad",
            "processed_adt.h5ad",
            "unfiltered_adt.h5ad",
        ]

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=file_name,
            sample=sample,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                readme_file_path,
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
                    file_folder = sample.project.get_sample_input_data_dir(sample.scpca_id)
                    file_name = f"{library['scpca_library_id']}_{file_suffix}"
                    file_path = file_folder / file_name
                    file_paths.append(file_path)
                    zip_file.write(file_path, file_name)

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = sample.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size
        computed_file.includes_celltype_report = includes_celltype_report

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
        return (
            self.modality == ComputedFile.OutputFileModalities.SINGLE_CELL
            and self.has_multiplexed_data
        )

    @property
    def is_project_single_cell_zip(self):
        return (
            self.modality == ComputedFile.OutputFileModalities.SINGLE_CELL
            and not self.has_multiplexed_data
        )

    @property
    def is_project_spatial_zip(self):
        return self.modality == ComputedFile.OutputFileModalities.SPATIAL

    @property
    def metadata_file_name(self):
        if self.is_project_multiplexed_zip or self.is_project_single_cell_zip:
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

    def upload_s3_file(self):
        """Uploads the computed file to S3 using AWS CLI tool."""

        logger.info(f"Uploading {self}")
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

    def process_computed_file(self, clean_up_output_data, update_s3):
        """Processes saving, upload and cleanup of a single computed file."""
        self.save()
        if update_s3:
            self.upload_s3_file()

        # Don't clean up multiplexed sample zips until the project is done
        is_multiplexed_sample = self.sample and self.sample.has_multiplexed_data

        if clean_up_output_data and not is_multiplexed_sample:
            self.zip_file_path.unlink(missing_ok=True)

        # Close DB connection for each thread.
        connection.close()
