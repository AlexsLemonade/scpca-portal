from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from typing_extensions import Self

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class DownloadableFileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_downloadable=True)


class OriginalFile(TimestampedModel):
    class Meta:
        db_table = "original_files"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    # s3 info
    s3_bucket = models.TextField()
    s3_key = models.TextField()
    size_in_bytes = models.BigIntegerField()
    hash = models.CharField(max_length=33)
    hash_change_at = models.DateTimeField()
    bucket_sync_at = models.DateTimeField()

    # inferred relationship ids
    project_id = models.TextField(null=True)
    sample_ids = ArrayField(models.TextField(null=True), default=list)
    library_id = models.TextField(null=True)

    # existence attributes
    # modalities
    is_single_cell = models.BooleanField(default=False)
    is_spatial = models.BooleanField(default=False)
    is_cite_seq = models.BooleanField(default=False)  # indicates if file is exclusively cite_seq
    is_bulk = models.BooleanField(default=False)
    # formats
    formats = ArrayField(models.TextField(choices=FileFormats.choices), default=list)
    is_single_cell_experiment = models.BooleanField(default=False)
    is_anndata = models.BooleanField(default=False)
    is_spatial_spaceranger = models.BooleanField(default=False)
    is_metadata = models.BooleanField(default=False)
    is_supplementary = models.BooleanField(default=False)
    # other
    is_merged = models.BooleanField(default=False)
    is_project_file = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    # queryset managers
    objects = models.Manager()
    downloadable_objects = DownloadableFileManager()

    def __str__(self):
        return f"Original File {self.s3_key} from Project {self.project_id} ({self.size_in_bytes}B)"

    @classmethod
    def get_from_dict(cls, file_object, bucket, sync_timestamp):
        s3_key_info = utils.InputBucketS3KeyInfo(Path(file_object["s3_key"]))
        modalities = s3_key_info.modalities
        formats = s3_key_info.formats

        original_file = cls(
            s3_bucket=bucket,
            s3_key=file_object["s3_key"],
            size_in_bytes=file_object["size_in_bytes"],
            hash=file_object["hash"],
            hash_change_at=sync_timestamp,
            bucket_sync_at=sync_timestamp,
            project_id=s3_key_info.project_id,
            sample_ids=s3_key_info.sample_ids,
            library_id=s3_key_info.library_id,
            is_single_cell=(Modalities.SINGLE_CELL in modalities),
            is_spatial=(Modalities.SPATIAL in modalities),
            is_cite_seq=(Modalities.CITE_SEQ in modalities),
            is_bulk=(Modalities.BULK_RNA_SEQ in modalities),
            formats=formats,
            is_single_cell_experiment=(FileFormats.SINGLE_CELL_EXPERIMENT in formats),
            is_anndata=(FileFormats.ANN_DATA in formats),
            is_spatial_spaceranger=(FileFormats.SPATIAL_SPACERANGER in formats),
            is_metadata=(FileFormats.METADATA in formats),
            is_supplementary=(FileFormats.SUPPLEMENTARY in formats),
            is_merged=s3_key_info.is_merged,
            is_project_file=s3_key_info.is_project_file,
            is_downloadable=OriginalFile._is_downloadable(s3_key_info),
        )

        return original_file

    @staticmethod
    def _is_downloadable(s3_key_info: utils.InputBucketS3KeyInfo):
        """
        Returns whether or not a file is downloadable.
        Most files are downloadable, with the exception of input metadata files.
        """
        if Modalities.SPATIAL in s3_key_info.modalities:
            # Spatial input metadata files are downloadable (an exception to the rule)
            return True

        if FileFormats.METADATA in s3_key_info.formats:
            # the bulk metadata file is downloadable, while all others are not
            return Modalities.BULK_RNA_SEQ in s3_key_info.modalities

        return True

    @classmethod
    def bulk_create_from_dicts(cls, file_objects, bucket, sync_timestamp) -> List[Self]:
        original_files = []
        for file_object in file_objects:
            if not OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).exists():
                original_files.append(
                    OriginalFile.get_from_dict(file_object, bucket, sync_timestamp)
                )

        return OriginalFile.objects.bulk_create(original_files)

    @classmethod
    def bulk_update_from_dicts(
        cls, file_objects: List[Dict], bucket: str, sync_timestamp
    ) -> List[Self]:
        # all existing files must have their timestamps updated, at the minimum
        existing_original_files = []
        # existing files that have been modified should be collected and returned separately
        modified_original_files = []
        fields = set()

        for file_object in file_objects:
            if original_instance := OriginalFile.objects.filter(
                s3_bucket=bucket, s3_key=file_object["s3_key"]
            ).first():
                if original_instance.hash != file_object["hash"]:
                    original_instance.hash = file_object["hash"]
                    original_instance.hash_change_at = sync_timestamp
                    original_instance.size_in_bytes = file_object["size_in_bytes"]
                    fields.update({"hash", "hash_change_at", "size_in_bytes"})

                    modified_original_files.append(original_instance)

                # all existing objects with files still on s3 must have their timestamps updated
                original_instance.bucket_sync_at = sync_timestamp
                fields.add("bucket_sync_at")

                existing_original_files.append(original_instance)

        # check that file_objects are not all new files (bulk_update will fail with an empty list)
        if existing_original_files:
            OriginalFile.objects.bulk_update(existing_original_files, fields)

        return modified_original_files

    @staticmethod
    def purge_deleted_files(
        bucket: str, sync_timestamp, allow_bucket_wipe: bool = False
    ) -> List[Self]:
        """Purge all files that no longer exist on s3."""
        # if the last_bucket_sync timestamp wasn't updated,
        # then the file has been deleted from s3, which must be reflected in the db.
        deletable_files = OriginalFile.objects.filter(s3_bucket=bucket).exclude(
            bucket_sync_at=sync_timestamp
        )
        deletable_file_list = list(deletable_files)

        all_bucket_files = OriginalFile.objects.filter(s3_bucket=bucket)
        # if allow_bucket_wipe flag is not passed, do not allow all bucket files to be wiped
        if set(all_bucket_files) == set(deletable_files) and not allow_bucket_wipe:
            return []

        deletable_files.delete()
        return deletable_file_list

    @property
    def s3_key_info(self) -> utils.InputBucketS3KeyInfo:
        return utils.InputBucketS3KeyInfo(self.s3_key_path)

    @property
    def s3_key_path(self) -> Path:
        return Path(self.s3_key)

    @property
    def s3_bucket_path(self) -> Path:
        return Path(self.s3_bucket)

    @property
    def s3_absolute_path(self) -> Path:
        return self.s3_bucket_path / self.s3_key_path

    @property
    def download_dir(self) -> Path:
        """
        Return an original file's download directory.

        To produce more efficient downloads, files are downloaded as collections.
        Collections are formed as granularly as possible,
        at either the sample/merged/bulk, project, or bucket levels.
        """
        if sample_id_part := self.s3_key_info.sample_id_part:
            return Path(self.s3_key_info.project_id_part, sample_id_part)

        if project_id_part := self.s3_key_info.project_id:
            return Path(project_id_part)

        # default to bucket dir
        return Path()

    @property
    def download_path(self) -> Path:
        """Return the remaining part of self.s3_key that's not the download_dir."""
        return self.s3_key_path.relative_to(self.download_dir)

    @property
    def local_file_path(self):
        return settings.INPUT_DATA_PATH / self.s3_key_path

    def _get_zip_file_path(self, download_config: Dict) -> Path:
        """
        Return file path with requested directory structure according to download config.
        The multiplexed sample delimeter is not replaced in this method.
        """
        # Project output paths are relative to project directory
        output_path = self.s3_key_path.relative_to(Path(self.s3_key_info.project_id_part))

        # Sample output paths are relative to sample directory
        if download_config in common.SAMPLE_DOWNLOAD_CONFIGS.values():
            return output_path.relative_to(Path(self.s3_key_info.sample_id_part))

        # Transform merged and bulk project data files to no longer be nested in a merged directory
        if self.is_merged:
            return output_path.relative_to(common.MERGED_INPUT_DIR)
        if self.is_bulk:
            return output_path.relative_to(common.BULK_INPUT_DIR)

        # Nest sample reports into individual_reports directory in merged download
        # The merged summmary html file should not go into this directory
        if download_config.get("includes_merged", False) and self.is_supplementary:
            return Path(common.MERGED_REPORTS_PREFEX_DIR) / output_path

        return output_path

    def get_zip_file_path(self, download_config: Dict) -> Path:
        """Returns the formatted file path while replacing the multiplexed sample delimter."""
        # Delimeter must be exchanged if file has multiplexed samples
        return utils.path_replace(
            self._get_zip_file_path(download_config),
            common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER,
            common.MULTIPLEXED_SAMPLES_OUTPUT_DELIMETER,
        )

    @staticmethod
    def get_bucket_paths(original_files) -> Dict[Tuple, List[Path]]:
        """
        Collect and return files for download according to their bucket names and download dirs.
        """
        bucket_paths = defaultdict(list)
        for original_file in original_files:
            # if a file doesn't exist locally, then it should be downloaded
            if not original_file.s3_key_path.exists():
                bucket_paths[(original_file.s3_bucket_path, original_file.download_dir)].append(
                    original_file.download_path
                )

        return bucket_paths

    @classmethod
    def get_input_projects_metadata_file(
        cls, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> Self:
        return OriginalFile.objects.filter(
            is_metadata=True, project_id=None, s3_bucket=bucket
        ).first()

    @classmethod
    def get_input_samples_metadata_file(
        cls, project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> Self:
        return OriginalFile.objects.filter(
            is_metadata=True,
            is_bulk=False,
            project_id=project_id,
            sample_ids=[],
            library_id=None,
            s3_bucket=bucket,
        ).first()

    @classmethod
    def get_input_library_metadata_files(
        cls, project_id: str, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> Iterable[Self]:
        return OriginalFile.objects.filter(
            is_metadata=True,
            project_id=project_id,
            library_id__isnull=False,
            s3_key__endswith="_metadata.json",  # Exclude other .csv, .json files
            s3_bucket=bucket,
        )

    @classmethod
    def get_input_project_bulk_metadata_file(
        cls, project_id, *, bucket: str = settings.AWS_S3_INPUT_BUCKET_NAME
    ) -> Self:
        return OriginalFile.objects.filter(
            is_metadata=True, is_bulk=True, project_id=project_id, s3_bucket=bucket
        ).first()
