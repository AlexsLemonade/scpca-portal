from dataclasses import dataclass
from pathlib import Path

from scpca_portal import common, utils


@dataclass
class S3KeyInfo:
    s3_key: Path
    project_id: str | None
    sample_id: str | None
    library_id_part: str | None
    is_merged: bool
    is_bulk: bool

    def __init__(self, s3_key: Path):
        self.s3_key = s3_key
        self.project_id = utils.find_first_contained(common.PROJECT_ID_PREFIX, s3_key.parts)
        self.sample_id = utils.find_first_contained(common.SAMPLE_ID_PREFIX, s3_key.parts)
        self.library_id_part = utils.find_first_contained(common.LIBRARY_ID_PREFIX, s3_key.parts)
        self.is_merged = "merged" in s3_key.parts
        self.is_bulk = "bulk" in s3_key.parts

    @property
    def library_id(self):
        if self.library_id_part:
            return self.library_id_part.split("_")[0]
        return self.library_id_part

    @property
    def is_project_file(self):
        """Project files have project dirs but don't have sample dirs"""
        return bool(self.project_id and not self.sample_id)

    @property
    def is_spatial(self):
        # all spatial files have "spatial" appended to the libary part of their file path
        return bool(self.library_id_part and self.library_id_part.endswith("spatial"))

    @property
    def is_single_cell(self):
        # single cell files won't be nested in subdirectories
        return self.library_id_part == self.s3_key.name

    @property
    def is_cite_seq(self):
        return self.s3_key.name.endswith(common.CITE_SEQ_FILENAME_ENDING)

    @property
    def is_single_cell_experiment(self):
        return (
            self.s3_key.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]
            or self.is_spatial  # we consider all spatial files SCE
        )

    @property
    def is_anndata(self):
        return self.s3_key.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]

    @property
    def is_metadata(self):
        return self.s3_key.suffix in common.METADATA_EXTENSIONS

    @property
    def is_downloadable(self):
        """
        Returns whether or not a file is_downloadable.
        Most files are downloadable files,
        the only exceptions are single_cell metadata files and project level metadata files.
        """
        if self.is_single_cell:
            # single_cell metadata files are not included in computed files
            return not self.is_metadata

        return self.s3_key.name not in common.NON_DOWNLOADABLE_PROJECT_FILES
