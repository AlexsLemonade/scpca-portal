from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellSingleCellExperimentNoMultiplexedSCPCP999991:
    PROJECT_ID = "SCPCP999991"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "data": {
            PROJECT_ID: {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "data_hash": "48561ed4e00b7e9393acbdc4aff47155",
        "metadata_hash": "7da4a7245e0cca530e688ce1eeac7be6",
        "readme_hash": "a4d76619e39eb4b498b13acb9816b1ed",
        "combined_hash": "710ad8cef8645baa85f0315b4decf1d2",
        "includes_files_bulk": False,
        "includes_files_cite_seq": False,
        "includes_files_merged": False,
        "includes_files_multiplexed": False,
        "estimated_size_in_bytes": 3875,
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
        "is_terminated": False,
        "terminated_reason": None,
        "ccdl_name": CCDL_NAME,
        "ccdl_project_id": PROJECT_ID,
        "ccdl_modality": Modalities.SINGLE_CELL,
    }
