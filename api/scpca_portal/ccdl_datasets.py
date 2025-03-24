from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities

TYPES = {
    CCDLDatasetNames.ALL_METADATA: {
        "modality": None,
        "format": DatasetFormats.METADATA,
        "excludes_multiplexed": False,
        "includes_merged": False,
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": False,
        "includes_merged": False,
    },
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED: {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": True,
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA: {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.ANN_DATA,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
    CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED: {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.ANN_DATA,
        "excludes_multiplexed": True,
        "includes_merged": True,
    },
    CCDLDatasetNames.SPATIAL_SINGLE_CELL_EXPERIMENT: {
        "modality": Modalities.SPATIAL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
}

PORTAL_TYPE_NAMES = [
    "ALL_METADATA",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT",
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED",
    "SINGLE_CELL_ANN_DATA",
    "SINGLE_CELL_ANN_DATA_MERGED",
    "SPATIAL_SINGLE_CELL_EXPERIMENT",
    "SAMPLE_SINGLE_CELL_SINGLE_CELL_EXPERIMENT",
    "SAMPLE_SINGLE_CELL_ANN_DATA",
    "SAMPLE_SPATIAL_SINGLE_CELL_EXPERIMENT",
]
