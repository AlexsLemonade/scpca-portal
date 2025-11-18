from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetAllMetadata:
    CCDL_NAME = CCDLDatasetNames.ALL_METADATA.name
    VALUES = {
        "data": {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL.name: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.name: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL.name: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.name: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL.name: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.METADATA.name,
        "regenerated_from": None,
        "is_ccdl": True,
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
