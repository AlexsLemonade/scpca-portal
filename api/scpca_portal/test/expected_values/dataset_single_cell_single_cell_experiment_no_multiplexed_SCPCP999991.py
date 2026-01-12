from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetSingleCellSingleCellExperimentNoMultiplexedSCPCP999991:
    PROJECT_ID = "SCPCP999991"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED.value
    VALUES = {
        "data": {
            PROJECT_ID: {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "regenerated_from": None,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": PROJECT_ID,
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
