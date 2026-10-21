from django.conf import settings

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellSingleCellExperimentSCPCP999994:
    PROJECT_ID = "SCPCP999994"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "data": {
            PROJECT_ID: {
                "includes_bulk": False,
                Modalities.SINGLE_CELL.value: ["SCPCS999988", "SCPCS999989"],
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
        "ccdl_is_merged": False,
    }
    COMPUTED_FILE_LIST = [
        "README.md",
        "SCPCP999994_single-cell/SCPCS999988/SCPCL999989-SCPCS999988_celltype-report.html",
        "SCPCP999994_single-cell/SCPCS999988/SCPCL999989-SCPCS999988_filtered.rds",
        "SCPCP999994_single-cell/SCPCS999988/SCPCL999989-SCPCS999988_processed.rds",
        "SCPCP999994_single-cell/SCPCS999988/SCPCL999989-SCPCS999988_qc.html",
        "SCPCP999994_single-cell/SCPCS999988/SCPCL999989-SCPCS999988_unfiltered.rds",
        "SCPCP999994_single-cell/SCPCS999989/SCPCL999989-SCPCS999989_celltype-report.html",
        "SCPCP999994_single-cell/SCPCS999989/SCPCL999989-SCPCS999989_filtered.rds",
        "SCPCP999994_single-cell/SCPCS999989/SCPCL999989-SCPCS999989_processed.rds",
        "SCPCP999994_single-cell/SCPCS999989/SCPCL999989-SCPCS999989_qc.html",
        "SCPCP999994_single-cell/SCPCS999989/SCPCL999989-SCPCS999989_unfiltered.rds",
        "SCPCP999994_single-cell/single-cell_metadata.tsv",
    ]
    COMPUTED_FILE_VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "has_bulk_rna_seq": False,
        "has_cite_seq_data": False,
        "has_multiplexed_data": False,
        "includes_merged": False,
        "modality": Modalities.SINGLE_CELL.value,
        "metadata_only": False,
        "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
        "size_in_bytes": 6759,
        "workflow_version": "v0.10.4",
        "includes_celltype_report": True,
    }
