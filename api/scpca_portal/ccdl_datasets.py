from scpca_portal.enums import DatasetFormats, Modalities

TYPES = {
    "ALL_METADATA": {
        "modality": None,
        "format": DatasetFormats.METADATA,
        "excludes_multiplexed": False,
        "includes_merged": False,
    },
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": False,
        "includes_merged": False,
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": True,
    },
    "SINGLE_CELL_ANN_DATA": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.ANN_DATA,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
    "SINGLE_CELL_ANN_DATA_MERGED": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.ANN_DATA,
        "excludes_multiplexed": True,
        "includes_merged": True,
    },
    "SPATIAL_SINGLE_CELL_EXPERIMENT": {
        "modality": Modalities.SPATIAL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        "excludes_multiplexed": True,
        "includes_merged": False,
    },
    "SAMPLE_SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
    },
    "SAMPLE_SINGLE_CELL_ANN_DATA": {
        "modality": Modalities.SINGLE_CELL,
        "format": DatasetFormats.ANN_DATA,
    },
    "SAMPLE_SPATIAL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SPATIAL",
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
    },
}

# List out CCDLDatasetNames for valid types for each scope
PORTAL_NAMES = []
PROJECT_NAMES = []
SAMPLE_NAMES = []
