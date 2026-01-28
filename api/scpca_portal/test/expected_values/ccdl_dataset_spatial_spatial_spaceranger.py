from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSpatialSpatialSpaceranger:
    CCDL_NAME = CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "data": {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: [],
                Modalities.SPATIAL.value: ["SCPCS999991"],
            },
        },
        "email": None,
        "start": False,
        "data_hash": "88d21df8a1995f9ac1c0687187005bd0",
        "metadata_hash": "f061ca5b7a46f22e8bf7fa249b0e3dec",
        "readme_hash": "0936530160ecd61d1455ebae739a26c8",
        "combined_hash": "3fc532e97aac201d8cb56fce3bfdf31a",
        "includes_files_bulk": False,
        "includes_files_cite_seq": False,
        "includes_files_merged": False,
        "includes_files_multiplexed": False,
        "estimated_size_in_bytes": 4354,
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
        "ccdl_modality": Modalities.SPATIAL,
    }
