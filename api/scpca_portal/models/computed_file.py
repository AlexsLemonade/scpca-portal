from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile

from django.conf import settings
from django.db import models

from typing_extensions import Self

from scpca_portal import common, readme_file, s3, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.exceptions import DatasetLockedProjectError, DatasetMissingLibrariesError
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.original_file import OriginalFile

if TYPE_CHECKING:
    from scpca_portal.models import CCDLDataset, DatasetABC


logger = get_and_configure_logger(__name__)


class ComputedFile(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "computed_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    class OutputFileModalities:
        SINGLE_CELL = "SINGLE_CELL"
        SPATIAL = "SPATIAL"

        CHOICES = (
            (SINGLE_CELL, "Single Cell"),
            (SPATIAL, "Spatial"),
        )

    class OutputFileFormats:
        ANN_DATA = "ANN_DATA"
        SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"
        SPATIAL_SPACERANGER = "SPATIAL_SPACERANGER"

        CHOICES = (
            (ANN_DATA, "AnnData"),
            (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
            (SPATIAL_SPACERANGER, "Spatial Spaceranger"),
        )

    format = models.TextField(choices=OutputFileFormats.CHOICES, null=True)
    includes_merged = models.BooleanField(default=False)
    modality = models.TextField(choices=OutputFileModalities.CHOICES, null=True)
    metadata_only = models.BooleanField(default=False)
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    workflow_version = models.TextField()
    includes_celltype_report = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (
            f"'{getattr(self, "ccdldataset", None) or getattr(self, "userdataset", None)}' "
            f"{dict(self.OutputFileModalities.CHOICES).get(self.modality, 'No Modality')} "
            f"{dict(self.OutputFileFormats.CHOICES).get(self.format, 'No Format')} "
            f"computed file ({self.size_in_bytes}B)"
        )

    @staticmethod
    def get_output_file_parent_dir(
        original_file: OriginalFile,
        dataset: "DatasetABC",
    ) -> Path:
        """Return the correct output file parent directory of the passed original_file."""
        if original_file.is_bulk:
            return Path(f"{original_file.project_id}_bulk")

        # spatial / unmerged single cell
        modality = Modalities.SINGLE_CELL if original_file.is_single_cell else Modalities.SPATIAL
        modality_formatted = modality.value.lower().replace("_", "-")
        parent_dir = Path(f"{original_file.project_id}_{modality_formatted}")

        # merged single cell
        # only single cell supplementary and merged files should be nested in a merge directory
        if dataset.get_is_merged_project(original_file.project_id) and not original_file.is_spatial:
            parent_dir = Path(f"{original_file.project_id}_single-cell_merged")

            # only library supplementary files should be in an individual_reports dir,
            # not the merged supplementary file
            if original_file.is_supplementary and not original_file.is_merged:
                return parent_dir / Path(common.MERGED_REPORTS_PREFEX_DIR)

        return parent_dir

    @staticmethod
    def get_original_file_zip_path(original_file: OriginalFile, dataset: "DatasetABC") -> Path:
        """Return an original file's path for the zip file being computed."""
        # always remove project directory
        zip_file_path = original_file.s3_key_path.relative_to(
            Path(original_file.s3_key_info.project_id_part)
        )
        if original_file.is_bulk or original_file.is_merged:
            # bulk and merged files come in nested directories, which should be popped off
            zip_file_path = Path(*zip_file_path.parts[1:])

        parent_dir = ComputedFile.get_output_file_parent_dir(original_file, dataset)
        zip_file_path = parent_dir / zip_file_path

        # Make sure that multiplexed sample files are adequately transformed by default
        return utils.path_replace(
            zip_file_path,
            common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER,
            common.MULTIPLEXED_SAMPLES_OUTPUT_DELIMETER,
        )

    @staticmethod
    def get_metadata_file_zip_path(
        dataset: "DatasetABC", project_id: str | None = None, modality: Modalities | None = None
    ) -> Path:
        """Return metadata file path, modality name inside of project_modality directory."""
        # Metadata only downloads are not associated with a specific project_id or modality
        if not project_id:
            return Path("metadata.tsv")

        modality_formatted = modality.value.lower().replace("_", "-")
        metadata_file_name_path = Path(f"{modality_formatted}_metadata.tsv")

        metadata_dir = f"{project_id}_{modality_formatted}"
        if dataset.get_is_merged_project(project_id):
            metadata_dir += "_merged"

        return Path(metadata_dir) / Path(metadata_file_name_path)

    @classmethod
    def get_dataset_file_s3_key(cls, dataset: "DatasetABC") -> str:
        return f"{dataset.id}.zip"

    # # TODO: TEMP translation for dataset -> computed file enums
    @classmethod
    def get_output_file_format(cls, dataset: "DatasetABC") -> str | None:
        match dataset.format:
            case DatasetFormats.SINGLE_CELL_EXPERIMENT:
                if (
                    type(dataset).__name__ == "CCDLDataset"
                    and dataset.ccdl_modality == Modalities.SPATIAL
                ):
                    return cls.OutputFileFormats.SPATIAL_SPACERANGER
                else:
                    return cls.OutputFileFormats.SINGLE_CELL_EXPERIMENT
            case DatasetFormats.ANN_DATA:
                return cls.OutputFileFormats.ANN_DATA
            case DatasetFormats.METADATA:
                return None
            case _:
                return None

    @classmethod
    def get_ccdl_dataset_output_file_modality(cls, dataset: "CCDLDataset") -> str | None:
        match dataset.ccdl_type.get("modality"):
            case Modalities.SINGLE_CELL:
                return cls.OutputFileModalities.SINGLE_CELL
            case Modalities.SPATIAL:
                return cls.OutputFileModalities.SPATIAL
            case _:
                return None

    @classmethod
    def get_dataset_file(cls, dataset: "DatasetABC") -> Self:
        """
        Computes a given dataset's zip archive and returns a corresponding ComputedFile object.
        """
        if dataset.is_locked:
            raise DatasetLockedProjectError(dataset)

        # If the query returns empty, then throw an error occurred.
        if not dataset.libraries.exists():
            raise DatasetMissingLibrariesError(dataset)

        dataset_original_files = dataset.original_files
        for project in dataset.projects:
            s3.download_files(dataset_original_files.filter(project_id=project.scpca_id))
            if dataset.is_locked:
                raise DatasetLockedProjectError(dataset)

        with ZipFile(dataset.computed_file_local_path, "w") as zip_file:
            # Readme file
            zip_file.writestr(readme_file.OUTPUT_NAME, dataset.readme_file_contents)

            # Metadata files
            for project_id, modality, metadata_file_content in dataset.get_metadata_file_contents():
                zip_file.writestr(
                    str(ComputedFile.get_metadata_file_zip_path(dataset, project_id, modality)),
                    metadata_file_content,
                )

            # Original files
            for original_file in dataset.original_files:
                zip_file.write(
                    original_file.local_file_path,
                    ComputedFile.get_original_file_zip_path(original_file, dataset),
                )

        computed_file = cls(
            has_bulk_rna_seq=(
                any(
                    True
                    for project_id, project_config in dataset.data.items()
                    if project_config.get("includes_bulk")
                    and dataset.projects.filter(scpca_id=project_id, has_bulk_rna_seq=True).exists()
                )
            ),
            has_cite_seq_data=dataset.libraries.filter(has_cite_seq_data=True).exists(),
            has_multiplexed_data=dataset.libraries.filter(is_multiplexed=True).exists(),
            format=cls.get_output_file_format(dataset),
            includes_celltype_report=dataset.projects.filter(samples__is_cell_line=False).exists(),
            includes_merged=dataset.includes_files_merged,
            modality=(
                cls.get_ccdl_dataset_output_file_modality(dataset)
                if type(dataset).__name__ == "CCDLDataset"
                else None
            ),
            metadata_only=dataset.format == DatasetFormats.METADATA,
            s3_bucket=settings.AWS_S3_OUTPUT_BUCKET_NAME,
            s3_key=cls.get_dataset_file_s3_key(dataset),
            size_in_bytes=dataset.computed_file_local_path.stat().st_size,
            workflow_version=utils.join_workflow_versions(
                library.workflow_version for library in dataset.libraries
            ),
        )
        dataset.computed_file = computed_file

        return computed_file

    def get_dataset_download_url(self, download_filename: str) -> str | None:
        """Return the presigned url on the associated dataset according to the passed filename."""
        if not (self.s3_bucket and self.s3_key):
            return None

        return s3.generate_pre_signed_link(download_filename, self.s3_key, self.s3_bucket)

    @property
    def download_filename(self) -> str:
        # Append the download date to the filename on download.
        date = utils.get_today_string()
        key_path = Path(self.s3_key)
        return f"{key_path.stem}_{date}{key_path.suffix}"

    @property
    def download_url(self) -> str:
        """A temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            return s3.generate_pre_signed_link(self.download_filename, self.s3_key, self.s3_bucket)

    @property
    def zip_file_path(self) -> Path:
        return settings.OUTPUT_DATA_PATH / self.s3_key

    def clean_up_local_computed_file(self) -> None:
        """Delete local computed file."""
        self.zip_file_path.unlink(missing_ok=True)

    def purge(self, delete_from_s3: bool = False) -> None:
        """Purges a computed file, optionally deleting it from S3."""
        if delete_from_s3:
            s3.delete_output_file(self.s3_key, self.s3_bucket)
        self.delete()
