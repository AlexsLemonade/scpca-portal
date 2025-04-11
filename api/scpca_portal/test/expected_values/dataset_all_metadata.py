from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetAllMetadata:
    CCDL_NAME = CCDLDatasetNames.ALL_METADATA.value
    VALUES = {
        "data": {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL.value: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999992": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.METADATA.value,
        "regenerated_from": None,
        "is_ccdl": True,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": None,
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
