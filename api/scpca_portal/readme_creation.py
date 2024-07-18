from typing import Dict

from scpca_portal import common

OUTPUT_README_FILE_NAME = "README.md"

README_ANNDATA_FILE_NAME = "readme_anndata.md"
README_ANNDATA_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_FILE_NAME

README_ANNDATA_MERGED_FILE_NAME = "readme_anndata_merged.md"
README_ANNDATA_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_MERGED_FILE_NAME

README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

README_SINGLE_CELL_MERGED_FILE_NAME = "readme_single_cell_merged.md"
README_SINGLE_CELL_MERGED_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_MERGED_FILE_NAME

README_METADATA_NAME = "readme_metadata_only.md"
README_METADATA_PATH = common.OUTPUT_DATA_PATH / README_METADATA_NAME

README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

README_SPATIAL_FILE_NAME = "readme_spatial.md"
README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
README_TEMPLATE_ANNDATA_MERGED_FILE_PATH = README_TEMPLATE_PATH / "anndata_merged.md"
README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
README_TEMPLATE_SINGLE_CELL_MERGED_FILE_PATH = README_TEMPLATE_PATH / "single_cell_merged.md"
README_TEMPLATE_METADATA_PATH = README_TEMPLATE_PATH / "metadata_only.md"
README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"


def get_readme_from_download_config(download_config: Dict):
    match download_config:
        case {"metadata_only": True}:
            return README_METADATA_PATH
        case {"excludes_multiplexed": False}:
            return README_MULTIPLEXED_FILE_PATH
        case {"format": "ANN_DATA", "includes_merged": True}:
            return README_ANNDATA_MERGED_FILE_PATH
        case {"modality": "SINGLE_CELL", "includes_merged": True}:
            return README_SINGLE_CELL_MERGED_FILE_PATH
        case {"format": "ANN_DATA"}:
            return README_ANNDATA_FILE_PATH
        case {"modality": "SINGLE_CELL"}:
            return README_SINGLE_CELL_FILE_PATH
        case {"modality": "SPATIAL"}:
            return README_SPATIAL_FILE_PATH
