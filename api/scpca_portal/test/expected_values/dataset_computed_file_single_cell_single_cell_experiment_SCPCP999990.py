from django.conf import settings

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class DatasetComputedFileSingleCellSingleCellExperimentSCPCP999990:
    PROJECT_ID = "SCPCP999990"
    CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
    FILE_LIST = [
        "README.md",
        "SCPCP999990_bulk_metadata.tsv",
        "SCPCP999990_bulk_quant.tsv",
        "SCPCS999990/SCPCL999990_celltype-report.html",
        "SCPCS999990/SCPCL999990_filtered.rds",
        "SCPCS999990/SCPCL999990_processed.rds",
        "SCPCS999990/SCPCL999990_qc.html",
        "SCPCS999990/SCPCL999990_unfiltered.rds",
        "SCPCS999997/SCPCL999997_celltype-report.html",
        "SCPCS999997/SCPCL999997_filtered.rds",
        "SCPCS999997/SCPCL999997_processed.rds",
        "SCPCS999997/SCPCL999997_qc.html",
        "SCPCS999997/SCPCL999997_unfiltered.rds",
        "single_cell_metadata.tsv",
    ]
    VALUES = {
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "has_bulk_rna_seq": True,
        "has_cite_seq_data": False,
        "has_multiplexed_data": False,
        "includes_merged": False,
        "modality": Modalities.SINGLE_CELL.value,
        "metadata_only": False,
        "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
        "s3_key": "SCPCP999990_SINGLE-CELL_SINGLE-CELL-EXPERIMENT.zip",
        "size_in_bytes": 9113,
        "workflow_version": "development",
        "includes_celltype_report": True,
    }
