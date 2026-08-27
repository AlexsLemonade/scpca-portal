from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSpatialSpatialSpacerangerSCPCP999990:
    PROJECT_ID = "SCPCP999990"
    CCDL_NAME = CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "data": {
            PROJECT_ID: {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: ["SCPCS999991"],
            }
        },
        "email": None,
        "start": False,
        "data_hash": None,
        "metadata_hash": None,
        "readme_hash": None,
        "combined_hash": None,
        "includes_files_bulk": None,
        "includes_files_cite_seq": None,
        "includes_files_merged": None,
        "includes_files_multiplexed": None,
        "estimated_size_in_bytes": None,
        "state": None,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": PROJECT_ID,
        "ccdl_modality": None,
        "ccdl_is_merged": False,
    }
