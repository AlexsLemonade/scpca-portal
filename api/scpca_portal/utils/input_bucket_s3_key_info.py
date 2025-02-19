from pathlib import Path
from typing import List

from scpca_portal import common, utils
from scpca_portal.enums import FileFormats, Modalities


class InputBucketS3KeyInfo:
    def __init__(self, s3_key: Path):
        self.s3_key: Path = s3_key
        self.project_id: str | None = utils.find_first_contained(
            common.PROJECT_ID_PREFIX, s3_key.parts
        )
        self.sample_id: str | None = utils.find_first_contained(
            common.SAMPLE_ID_PREFIX, s3_key.parts
        )
        self.library_id_part: str | None = utils.find_first_contained(
            common.LIBRARY_ID_PREFIX, s3_key.parts
        )

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
    def is_merged(self):
        return "merged" in self.s3_key.parts

    @property
    def modalities(self) -> List[Modalities]:
        modalities = []

        if self._is_single_cell:
            modalities.append(Modalities.SINGLE_CELL)
        if self._is_spatial:
            modalities.append(Modalities.SPATIAL)
        if self._is_cite_seq:
            modalities.append(Modalities.CITE_SEQ)
        if self._is_bulk:
            modalities.append(Modalities.BULK_RNA_SEQ)

        return modalities

    @property
    def format(self):
        if self._is_single_cell_experiment:
            return FileFormats.SINGLE_CELL_EXPERIMENT
        if self._is_anndata:
            return FileFormats.ANN_DATA
        if self._is_supplementary:
            return FileFormats.SUPPLEMENTARY
        if self._is_metadata:
            return FileFormats.METADATA

        return None

    @property
    def _is_spatial(self):
        # all spatial files have "spatial" appended to the libary part of their file path
        return bool(self.library_id_part and self.library_id_part.endswith("spatial"))

    @property
    def _is_single_cell(self):
        # single cell files won't be nested in subdirectories
        return self.library_id_part == self.s3_key.name

    @property
    def _is_cite_seq(self):
        return self.s3_key.name.endswith(common.CITE_SEQ_FILENAME_ENDING)

    @property
    def _is_bulk(self):
        return "bulk" in self.s3_key.parts

    @property
    def _is_single_cell_experiment(self):
        return (
            self.s3_key.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]
            or self._is_spatial  # we consider all spatial files SCE
        )

    @property
    def _is_anndata(self):
        return self.s3_key.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]

    @property
    def _is_supplementary(self):
        return self.s3_key.suffix in common.SUPPLEMENTARY_EXTENSIONS

    @property
    def _is_metadata(self):
        return self.s3_key.suffix in common.METADATA_EXTENSIONS
