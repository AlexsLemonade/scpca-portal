from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetSingleCellSingleCellExperimentMerged:
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.value
    VALUES = {
        "data": {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999992": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "regenerated_from": None,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": None,
        "started_at": None,
        "is_started": False,
        "is_processing": False,
        "succeeded_at": None,
        "is_succeeded": False,
        "failed_at": None,
        "is_failed": False,
        "failed_reason": None,
        "expires_at": None,
        "is_expired": False,
    }
