from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities

TYPES = {
    CCDLDatasetNames.ALL_METADATA.name: {
        "modality": None,
        "format": DatasetFormats.METADATA.name,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "constraints": {},
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.name: {
        "modality": Modalities.SINGLE_CELL.name,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.name,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "constraints": {"has_single_cell_data": True},
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED.name: {
        "modality": Modalities.SINGLE_CELL.name,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.name,
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
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.name: {
        "modality": Modalities.SINGLE_CELL.name,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.name,
        "excludes_multiplexed": True,
        "includes_merged": True,
        "constraints": {
            "has_single_cell_data": True,
            "includes_merged_sce": True,
        },
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA.name: {
        "modality": Modalities.SINGLE_CELL.name,
        "format": DatasetFormats.ANN_DATA.name,
        "excludes_multiplexed": True,
        "includes_merged": False,
        "constraints": {
            "has_single_cell_data": True,
            "includes_anndata": True,
        },
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.name: {
        "modality": Modalities.SINGLE_CELL.name,
        "format": DatasetFormats.ANN_DATA.name,
        "excludes_multiplexed": True,
        "includes_merged": True,
        "constraints": {
            "has_single_cell_data": True,
            "includes_merged_anndata": True,
        },
    },
    CCDLDatasetNames.SPATIAL_SINGLE_CELL_EXPERIMENT.name: {
        "modality": Modalities.SPATIAL.name,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.name,
        "excludes_multiplexed": True,
        "includes_merged": False,
        "constraints": {
            "has_spatial_data": True,
        },
    },
}


PORTAL_TYPE_NAMES = [
    CCDLDatasetNames.ALL_METADATA.name,
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.name,
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.name,
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA.name,
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.name,
    CCDLDatasetNames.SPATIAL_SINGLE_CELL_EXPERIMENT.name,
]
