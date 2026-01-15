from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetAllMetadataSCPCP999990:
    PROJECT_ID = "SCPCP999990"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "data": {
            PROJECT_ID: {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL.value: [],
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
        "terminated_at": None,
        "is_terminated": None,
        "terminated_reason": None,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": PROJECT_ID,
        "ccdl_modality": None,
    }
