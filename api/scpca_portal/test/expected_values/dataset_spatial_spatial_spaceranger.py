from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetSpatialSpatialSpaceranger:
    CCDL_NAME = CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value
    VALUES = {
        "data": {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: ["SCPCS999991"],
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
