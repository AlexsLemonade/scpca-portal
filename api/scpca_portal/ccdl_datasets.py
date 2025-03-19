TYPES = {
    "ALL_METADATA": {
        "modality": None,
        "format": None,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": True,
    },
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": False,
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    "SINGLE_CELL_ANN_DATA": {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "SINGLE_CELL_ANN_DATA_MERGED": {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    "SPATIAL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SPATIAL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "SAMPLE_SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
    },
    "SAMPLE_SINGLE_CELL_ANN_DATA": {"modality": "SINGLE_CELL", "format": "ANN_DATA"},
    "SAMPLE_SPATIAL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SPATIAL",
        "format": "SINGLE_CELL_EXPERIMENT",
    },
}

# List out CCDLDatasetNames for valid types for each scope
PORTAL_NAMES = []
PROJECT_NAMES = []
SAMPLE_NAMES = []
