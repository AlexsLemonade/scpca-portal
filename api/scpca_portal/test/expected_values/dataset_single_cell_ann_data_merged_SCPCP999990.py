from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetSingleCellAnndataMergedSCPCP999990:
    PROJECT_ID = "SCPCP999990"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value
    VALUES = {
        "data": {
            PROJECT_ID: {
                "merge_single_cell": True,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL.value: [],
            }
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.ANN_DATA.value,
        "regenerated_from": None,
        "is_ccdl": True,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": PROJECT_ID,
        "started_at": None,
        "is_started": False,
        "is_processing": False,
        "processed_at": None,
        "is_processed": False,
        "errored_at": None,
        "is_errored": False,
        "error_message": None,
        "expires_at": None,
        "is_expired": False,
    }
