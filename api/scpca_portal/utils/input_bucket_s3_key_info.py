from pathlib import Path
from typing import List

from scpca_portal import common, utils
from scpca_portal.enums import FileFormats, Modalities


class InputBucketS3KeyInfo:
    def __init__(self, s3_key_path: Path):
        self.s3_key_path: Path = s3_key_path
        self.project_id_part: str | None = utils.find_first_contained(
            common.PROJECT_ID_PREFIX, s3_key_path.parts
        )
        self.sample_id_part: str | None = utils.find_first_contained(
            common.SAMPLE_ID_PREFIX, s3_key_path.parts
        )
        self.library_id_part: str | None = utils.find_first_contained(
            common.LIBRARY_ID_PREFIX, s3_key_path.parts
        )

    @property
    def project_id(self) -> str | None:
        return self.project_id_part

    @property
    def sample_ids(self) -> List[str]:
        if self.sample_id_part:
            return self.sample_id_part.split(common.MULTIPLEXED_SAMPLES_INPUT_DELIMETER)
        return []

    @property
    def library_id(self) -> str | None:
        if self.library_id_part:
            return self.library_id_part.split("_")[0]
        return self.library_id_part

    @property
    def is_project_file(self) -> bool:
        """Project files have project dirs but don't have sample dirs"""
        return bool(self.project_id_part and not self.sample_id_part)

    @property
    def is_merged(self) -> bool:
        return "merged" in self.s3_key_path.parts

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
    def formats(self) -> List[FileFormats]:
        formats = []

        if self._is_single_cell_experiment:
            formats.append(FileFormats.SINGLE_CELL_EXPERIMENT)
        if self._is_anndata:
            formats.append(FileFormats.ANN_DATA)
        if self._is_spatial_spaceranger:
            formats.append(FileFormats.SPATIAL_SPACERANGER)
        if self._is_metadata:
            formats.append(FileFormats.METADATA)
        if self._is_supplementary:
            formats.append(FileFormats.SUPPLEMENTARY)

        return formats

    @property
    def _is_spatial(self):
        # all spatial files have "spatial" appended to the libary part of their file path
        return bool(self.library_id_part and self.library_id_part.endswith("spatial"))

    @property
    def _is_single_cell(self):
        # single cell files won't be nested in subdirectories
        return self.library_id_part == self.s3_key_path.name

    @property
    def _is_cite_seq(self):
        return self.s3_key_path.name.endswith(common.CITE_SEQ_FILENAME_ENDING)

    @property
    def _is_bulk(self):
        return "bulk" in self.s3_key_path.parts

    @property
    def _is_single_cell_experiment(self):
        return self.s3_key_path.suffix == common.FORMAT_EXTENSIONS["SINGLE_CELL_EXPERIMENT"]

    @property
    def _is_anndata(self):
        return self.s3_key_path.suffix == common.FORMAT_EXTENSIONS["ANN_DATA"]

    @property
    def _is_spatial_spaceranger(self):
        return self._is_spatial

    @property
    def _is_metadata(self):
        return self.s3_key_path.stem.endswith("metadata")

    @property
    def _is_supplementary(self):
        return self.s3_key_path.suffix in common.SUPPLEMENTARY_EXTENSIONS
