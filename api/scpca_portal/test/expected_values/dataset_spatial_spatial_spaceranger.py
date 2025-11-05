from scpca_portal.enums import CCDLDatasetNames, FileFormats, Modalities


class DatasetSpatialSpatialSpaceranger:
    CCDL_NAME = CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value
    VALUES = {
        "data": {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999992": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "format": FileFormats.SPATIAL_SPACERANGER.value,
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
