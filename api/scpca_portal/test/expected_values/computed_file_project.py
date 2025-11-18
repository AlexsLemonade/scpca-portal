from django.conf import settings

from scpca_portal import common
from scpca_portal.models import ComputedFile


class Computed_File_Project:
    class SINGLE_CELL_SCE:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990", "SCPCL999997"}
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
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_SINGLE-CELL_SINGLE-CELL-EXPERIMENT.zip",
            "size_in_bytes": 9025,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class SINGLE_CELL_SCE_MULTIPLEXED:
        PROJECT_ID = "SCPCP999991"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999992", "SCPCL999995"}
        FILE_LIST = [
            "README.md",
            "SCPCS999992_SCPCS999993/SCPCL999992_celltype-report.html",
            "SCPCS999992_SCPCS999993/SCPCL999992_filtered.rds",
            "SCPCS999992_SCPCS999993/SCPCL999992_processed.rds",
            "SCPCS999992_SCPCS999993/SCPCL999992_qc.html",
            "SCPCS999992_SCPCS999993/SCPCL999992_unfiltered.rds",
            "SCPCS999995/SCPCL999995_celltype-report.html",
            "SCPCS999995/SCPCL999995_filtered.rds",
            "SCPCS999995/SCPCL999995_processed.rds",
            "SCPCS999995/SCPCL999995_qc.html",
            "SCPCS999995/SCPCL999995_unfiltered.rds",
            "single_cell_metadata.tsv",
        ]
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999991_SINGLE-CELL_SINGLE-CELL-EXPERIMENT_MULTIPLEXED.zip",
            "size_in_bytes": 9467,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class SINGLE_CELL_SCE_MERGED:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990", "SCPCL999997"}
        FILE_LIST = [
            "README.md",
            "SCPCP999990_bulk_metadata.tsv",
            "SCPCP999990_bulk_quant.tsv",
            "SCPCP999990_merged-summary-report.html",
            "SCPCP999990_merged.rds",
            "individual_reports/SCPCS999990/SCPCL999990_celltype-report.html",
            "individual_reports/SCPCS999990/SCPCL999990_qc.html",
            "individual_reports/SCPCS999997/SCPCL999997_celltype-report.html",
            "individual_reports/SCPCS999997/SCPCL999997_qc.html",
            "single_cell_metadata.tsv",
        ]
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": True,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_SINGLE-CELL_SINGLE-CELL-EXPERIMENT_MERGED.zip",
            "size_in_bytes": 8422,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class SINGLE_CELL_ANN_DATA:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_ANN_DATA"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990", "SCPCL999997"}
        FILE_LIST = [
            "README.md",
            "SCPCP999990_bulk_metadata.tsv",
            "SCPCP999990_bulk_quant.tsv",
            "SCPCS999990/SCPCL999990_celltype-report.html",
            "SCPCS999990/SCPCL999990_filtered_rna.h5ad",
            "SCPCS999990/SCPCL999990_processed_rna.h5ad",
            "SCPCS999990/SCPCL999990_qc.html",
            "SCPCS999990/SCPCL999990_unfiltered_rna.h5ad",
            "SCPCS999997/SCPCL999997_celltype-report.html",
            "SCPCS999997/SCPCL999997_filtered_rna.h5ad",
            "SCPCS999997/SCPCL999997_processed_rna.h5ad",
            "SCPCS999997/SCPCL999997_qc.html",
            "SCPCS999997/SCPCL999997_unfiltered_rna.h5ad",
            "single_cell_metadata.tsv",
        ]
        VALUES = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_SINGLE-CELL_ANN-DATA.zip",
            "size_in_bytes": 9440,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class SINGLE_CELL_ANN_DATA_MERGED:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_ANN_DATA_MERGED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990", "SCPCL999997"}
        FILE_LIST = [
            "README.md",
            "SCPCP999990_bulk_metadata.tsv",
            "SCPCP999990_bulk_quant.tsv",
            "SCPCP999990_merged-summary-report.html",
            "SCPCP999990_merged_rna.h5ad",
            "individual_reports/SCPCS999990/SCPCL999990_celltype-report.html",
            "individual_reports/SCPCS999990/SCPCL999990_qc.html",
            "individual_reports/SCPCS999997/SCPCL999997_celltype-report.html",
            "individual_reports/SCPCS999997/SCPCL999997_qc.html",
            "single_cell_metadata.tsv",
        ]
        VALUES = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": True,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_SINGLE-CELL_ANN-DATA_MERGED.zip",
            "size_in_bytes": 8548,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class SPATIAL_SINGLE_CELL_EXPERIMENT:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "SPATIAL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999991"}
        FILE_LIST = [
            "README.md",
            "SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json",
            "SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
            "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
            "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",
            "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
            "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
            "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
            "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
            "SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
            "SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
            "SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json",
            "SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png",
            "SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png",
            "SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv",
            "spatial_metadata.tsv",
        ]
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SPATIAL_SPACERANGER,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SPATIAL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_SPATIAL_SINGLE-CELL-EXPERIMENT.zip",
            "size_in_bytes": 8978,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }

    class ALL_METADATA:
        PROJECT_ID = "SCPCP999990"
        DOWNLOAD_CONFIG_NAME = "ALL_METADATA"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990", "SCPCL999991", "SCPCL999994", "SCPCL999997"}
        FILE_LIST = ["README.md", "metadata.tsv"]
        VALUES = {
            "format": None,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": None,
            "metadata_only": True,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": "SCPCP999990_ALL_METADATA.zip",
            "size_in_bytes": 5559,
            "workflow_version": "v0.8.7",
            "includes_celltype_report": True,
        }
