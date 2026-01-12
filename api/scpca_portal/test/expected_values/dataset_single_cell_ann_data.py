from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetSingleCellAnndata:
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value
    VALUES = {
        "data": {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999992": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.ANN_DATA.value,
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
