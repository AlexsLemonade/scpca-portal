from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellAnndataMerged:
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value
    VALUES = {
        "format": DatasetFormats.ANN_DATA.value,
        "data": {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
            "SCPCP999992": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",
                Modalities.SPATIAL.value: [],
            },
        },
        "email": None,
        "start": False,
        "data_hash": "dcd6070026971d4960d90df89399c2fb",
        "metadata_hash": "bf303b1f1ec8cc29bf882b13e8bc72ee",
        "readme_hash": "2a396b0f1086da707cb9a3221b5930ac",
        "combined_hash": "44225b9ea1c1e2eefd6b8881b0d1bf38",
        "includes_files_bulk": True,
        "includes_files_cite_seq": True,
        "includes_files_merged": True,
        "includes_files_multiplexed": False,
        "estimated_size_in_bytes": 9027,
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
        "ccdl_project_id": None,
        "ccdl_modality": Modalities.SINGLE_CELL,
    }
