from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities

# These types provide instructions for generating CCDL datasets
# Modality, format, excludes_multiplexed and includes_anndata for correct population of libraries
# Constants define datasets that would never have data included in them
TYPES = {
    CCDLDatasetNames.ALL_METADATA.value: {
        "modality": None,
        "format": DatasetFormats.METADATA.value,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "constraints": {},
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value: {
        "modality": Modalities.SINGLE_CELL.value,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "constraints": {"has_single_cell_data": True},
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED.value: {
        "modality": Modalities.SINGLE_CELL.value,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "excludes_multiplexed": True,
        "includes_merged": False,
        "constraints": {
            "has_single_cell_data": True,
            "has_multiplexed_data": True,
        },
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.value: {
        "modality": Modalities.SINGLE_CELL.value,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "excludes_multiplexed": True,
        "includes_merged": True,
        "constraints": {
            "has_single_cell_data": True,
            "includes_merged_sce": True,
        },
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value: {
        "modality": Modalities.SINGLE_CELL.value,
        "format": DatasetFormats.ANN_DATA.value,
        "excludes_multiplexed": True,
        "includes_merged": False,
        "constraints": {
            "has_single_cell_data": True,
            "includes_anndata": True,
        },
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value: {
        "modality": Modalities.SINGLE_CELL.value,
        "format": DatasetFormats.ANN_DATA.value,
        "excludes_multiplexed": True,
        "includes_merged": True,
        "constraints": {
            "has_single_cell_data": True,
            "includes_merged_anndata": True,
        },
    },
    CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value: {
        "modality": Modalities.SPATIAL.value,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,  # dataset format
        "excludes_multiplexed": True,
        "includes_merged": False,
        "constraints": {
            "has_spatial_data": True,
        },
    },
}


PORTAL_TYPE_NAMES = [
    CCDLDatasetNames.ALL_METADATA.value,
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value,
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.value,
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value,
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value,
    CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value,
]
