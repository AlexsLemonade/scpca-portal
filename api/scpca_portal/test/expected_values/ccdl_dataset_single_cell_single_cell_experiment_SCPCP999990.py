from django.conf import settings

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class CCDLDatasetSingleCellSingleCellExperimentSCPCP999990:
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
    COMPUTED_FILE_LIST = [
        "README.md",
        "SCPCP999990_bulk_rna/SCPCP999990_bulk_metadata.tsv",
        "SCPCP999990_bulk_rna/SCPCP999990_bulk_quant.tsv",
        "SCPCP999990_single-cell/SCPCS999990/SCPCL999990_celltype-report.html",
        "SCPCP999990_single-cell/SCPCS999990/SCPCL999990_filtered.rds",
        "SCPCP999990_single-cell/SCPCS999990/SCPCL999990_processed.rds",
        "SCPCP999990_single-cell/SCPCS999990/SCPCL999990_qc.html",
        "SCPCP999990_single-cell/SCPCS999990/SCPCL999990_unfiltered.rds",
        "SCPCP999990_single-cell/SCPCS999997/SCPCL999997_celltype-report.html",
        "SCPCP999990_single-cell/SCPCS999997/SCPCL999997_filtered.rds",
        "SCPCP999990_single-cell/SCPCS999997/SCPCL999997_processed.rds",
        "SCPCP999990_single-cell/SCPCS999997/SCPCL999997_qc.html",
        "SCPCP999990_single-cell/SCPCS999997/SCPCL999997_unfiltered.rds",
        "SCPCP999990_single-cell/single-cell_metadata.tsv",
    ]
    COMPUTED_FILE_VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "has_bulk_rna_seq": True,
        "has_cite_seq_data": False,
        "has_multiplexed_data": False,
        "includes_merged": False,
        "modality": Modalities.SINGLE_CELL.value,
        "metadata_only": False,
        "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
        "size_in_bytes": 7496,
        "workflow_version": "v0.8.8",
        "includes_celltype_report": True,
    }
