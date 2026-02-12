from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellAnndata:
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value
    VALUES = {
        "format": DatasetFormats.ANN_DATA.value,
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
        "data_hash": "32cf7b914a81aec87f1897fd08bf3ce5",
        "metadata_hash": "bf303b1f1ec8cc29bf882b13e8bc72ee",
        "readme_hash": "3a09619010b6e4d69bd1d546a773a565",
        "combined_hash": "e6087fdf200805c4da93389e6bccc8e0",
        "includes_files_bulk": True,
        "includes_files_cite_seq": True,
        "includes_files_merged": False,
        "includes_files_multiplexed": False,
        "estimated_size_in_bytes": 9002,
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
