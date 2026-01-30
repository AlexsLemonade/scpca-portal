from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetAllMetadata:
    CCDL_NAME = CCDLDatasetNames.ALL_METADATA.name
    VALUES = {
        "format": DatasetFormats.METADATA.name,
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
        "data_hash": "d41d8cd98f00b204e9800998ecf8427e",
        "metadata_hash": "2aea7305cb98bfcf3fa7e47911971546",
        "readme_hash": "cadb6c070573ee8d7ab939def2e7bd5d",
        "combined_hash": "d6218e3b06cb7408fd7115935fcc9235",
        "includes_files_bulk": False,
        "includes_files_cite_seq": True,
        "includes_files_merged": False,
        "includes_files_multiplexed": True,
        "estimated_size_in_bytes": 7886,
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
        "ccdl_modality": None,
    }
