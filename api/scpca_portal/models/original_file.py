from pathlib import Path
from typing import Dict, List

from django.db import models

from typing_extensions import Self

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


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
    sample_id = models.TextField(null=True)
    library_id = models.TextField(null=True)

    # existence attributes
    # modalities
    is_single_cell = models.BooleanField(default=False)
    is_spatial = models.BooleanField(default=False)
    is_cite_seq = models.BooleanField(default=False)
    is_bulk = models.BooleanField(default=False)
    # formats
    is_single_cell_experiment = models.BooleanField(default=False)
    is_anndata = models.BooleanField(default=False)
    is_metadata = models.BooleanField(default=False)
    # other
    is_merged = models.BooleanField(default=False)
    is_project_file = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    def __str__(self):
        return f"Original File {self.s3_key} from Project {self.project_id} ({self.size_in_bytes}B)"

    @classmethod
    def get_from_dict(cls, file_object, bucket, sync_timestamp):
        s3_key = Path(file_object["s3_key"])

        relationship_ids = OriginalFile.get_relationship_ids(s3_key)
        existence_attrs = OriginalFile.get_existence_attributes(s3_key)

        original_file = cls(
            s3_bucket=bucket,
            s3_key=s3_key,
            size_in_bytes=file_object["size_in_bytes"],
            hash=file_object["hash"],
            hash_change_at=sync_timestamp,
            bucket_sync_at=sync_timestamp,
            project_id=relationship_ids["project_id"],
            sample_id=relationship_ids["sample_id"],
            library_id=relationship_ids["library_id"],
            is_single_cell=existence_attrs["is_single_cell"],
            is_spatial=existence_attrs["is_spatial"],
            is_cite_seq=existence_attrs["is_cite_seq"],
            is_bulk=existence_attrs["is_bulk"],
            is_single_cell_experiment=existence_attrs["is_single_cell_experiment"],
            is_anndata=existence_attrs["is_anndata"],
            is_metadata=existence_attrs["is_metadata"],
            is_merged=existence_attrs["is_merged"],
            is_project_file=existence_attrs["is_project_file"],
            is_downloadable=existence_attrs["is_downloadable"],
        )

        return original_file

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

    @staticmethod
    def get_relationship_ids(s3_key: Path) -> Dict:
        """Parses s3_key and returns project, sample and library ids."""
        project_id = next(
            (p for p in s3_key.parts if common.PROJECT_ID_PREFIX in p),
            None,  # the only file w.o. a project id path part should be the projects metadata file
        )
        sample_id = next((p for p in s3_key.parts if common.SAMPLE_ID_PREFIX in p), None)
        library_id = next(
            # library ids are prepended to files followed by an underscore
            (p.split("_")[0] for p in s3_key.parts if common.LIBRARY_ID_PREFIX in p),
            None,
        )

        return {"project_id": project_id, "sample_id": sample_id, "library_id": library_id}

    @staticmethod
    def get_existence_attributes(s3_key: Path) -> Dict[str, bool]:
        """
        Derive existence attributes based on the passed s3_key,
        and return attributes as Dict.
        """
        attrs = {
            # modalities
            "is_single_cell": False,
            "is_spatial": False,
            "is_cite_seq": False,
            "is_bulk": False,
            # formats
            "is_single_cell_experiment": False,
            "is_anndata": False,
            "is_metadata": False,
            # other
            "is_merged": False,
            "is_project_file": False,
            "is_downloadable": True,
        }

        # Set project_files attr first as other attrs are dependent on it
        attrs["is_project_file"] = next(  # project files will not have sample subdirectories
            (False for p in s3_key.parts if p.startswith(common.SAMPLE_ID_PREFIX)), True
        )

        # MODALITIES
        if not attrs["is_project_file"]:
            library_path_part = next(
                file_part
                for file_part in s3_key.parts
                if file_part.startswith(common.LIBRARY_ID_PREFIX)
            )
            # all spatial files have "spatial" appended to the libary part of their file path
            attrs["is_spatial"] = library_path_part.endswith("spatial")
            # spatial and single_cell are mutually exclusive
            attrs["is_single_cell"] = not attrs["is_spatial"]
            attrs["is_cite_seq"] = common.CITE_SEQ_FILE_SUFFIX in s3_key.name
        attrs["is_bulk"] = "bulk" in s3_key.parts

        # FORMATS
        attrs["is_single_cell_experiment"] = (
            s3_key.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]
            or attrs["is_spatial"]  # we consider all spatial files SCE
        )
        attrs["is_anndata"] = s3_key.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]
        attrs["is_metadata"] = s3_key.suffix in [".csv", ".json"]

        # OTHERS
        attrs["is_merged"] = "merged" in s3_key.parts
        if attrs["is_project_file"]:
            attrs["is_downloadable"] = s3_key.name not in common.NON_DOWNLOADABLE_PROJECT_FILES
        elif attrs["is_single_cell"]:
            attrs["is_downloadable"] = not attrs["is_metadata"]

        return attrs
