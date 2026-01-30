from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellSingleCellExperimentMerged:
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
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
        "data_hash": "960324cc4f40bd93668b7c2c3cdb2d6e",
        "metadata_hash": "bf303b1f1ec8cc29bf882b13e8bc72ee",
        "readme_hash": "4c3c93d86e94753b1cd20c29c69ac9bd",
        "combined_hash": "c606053a3799239c3fbb3f6c418cb04f",
        "includes_files_bulk": True,
        "includes_files_cite_seq": True,
        "includes_files_merged": True,
        "includes_files_multiplexed": False,
        "estimated_size_in_bytes": 9093,
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
