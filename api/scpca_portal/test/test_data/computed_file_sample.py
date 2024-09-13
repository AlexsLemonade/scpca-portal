from django.conf import settings

from scpca_portal import common
from scpca_portal.models import ComputedFile, Sample


class Computed_File_Sample:
    class SINGLE_CELL_SCE:
        PROJECT_ID = "SCPCP999990"
        SAMPLE_ID = "SCPCS999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.SAMPLE_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990"}
        FILE_LIST = [
            "README.md",
            "SCPCL999990_celltype-report.html",
            "SCPCL999990_filtered.rds",
            "SCPCL999990_processed.rds",
            "SCPCL999990_qc.html",
            "SCPCL999990_unfiltered.rds",
            "single_cell_metadata.tsv",
        ]
        OUTPUT_FILE_NAME = Sample.get_output_file_name(SAMPLE_ID, DOWNLOAD_CONFIG)
        SAMPLE_ZIP_PATH = common.OUTPUT_DATA_PATH / OUTPUT_FILE_NAME
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": OUTPUT_FILE_NAME,
            "size_in_bytes": 7089,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }

    class SINGLE_CELL_ANN_DATA:
        PROJECT_ID = "SCPCP999990"
        SAMPLE_ID = "SCPCS999990"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_ANN_DATA"
        DOWNLOAD_CONFIG = common.SAMPLE_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999990"}
        FILE_LIST = [
            "README.md",
            "SCPCL999990_celltype-report.html",
            "SCPCL999990_filtered_rna.h5ad",
            "SCPCL999990_processed_rna.h5ad",
            "SCPCL999990_qc.html",
            "SCPCL999990_unfiltered_rna.h5ad",
            "single_cell_metadata.tsv",
        ]
        OUTPUT_FILE_NAME = Sample.get_output_file_name(SAMPLE_ID, DOWNLOAD_CONFIG)
        SAMPLE_ZIP_PATH = common.OUTPUT_DATA_PATH / OUTPUT_FILE_NAME
        VALUES = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": OUTPUT_FILE_NAME,
            "size_in_bytes": 7401,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }

    class SPATIAL_SCE:
        PROJECT_ID = "SCPCP999990"
        SAMPLE_ID = "SCPCS999991"
        DOWNLOAD_CONFIG_NAME = "SPATIAL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.SAMPLE_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999991"}
        FILE_LIST = [
            "README.md",
            "SCPCL999991_spatial/SCPCL999991_metadata.json",
            "SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
            "SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
            "SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",
            "SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
            "SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
            "SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
            "SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
            "SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
            "SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
            "SCPCL999991_spatial/spatial/scalefactors_json.json",
            "SCPCL999991_spatial/spatial/tissue_hires_image.png",
            "SCPCL999991_spatial/spatial/tissue_lowres_image.png",
            "SCPCL999991_spatial/spatial/tissue_positions_list.csv",
            "spatial_metadata.tsv",
        ]
        OUTPUT_FILE_NAME = Sample.get_output_file_name(SAMPLE_ID, DOWNLOAD_CONFIG)
        SAMPLE_ZIP_PATH = common.OUTPUT_DATA_PATH / OUTPUT_FILE_NAME
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SPATIAL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": OUTPUT_FILE_NAME,
            "size_in_bytes": 8818,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }

    class MULTIPLEXED_SINGLE_CELL_SCE:
        PROJECT_ID = "SCPCP999991"
        SAMPLE_ID = "SCPCS999992"
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.SAMPLE_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        LIBRARIES = {"SCPCL999992"}
        FILE_LIST = [
            "README.md",
            "SCPCL999992_celltype-report.html",
            "SCPCL999992_filtered.rds",
            "SCPCL999992_processed.rds",
            "SCPCL999992_qc.html",
            "SCPCL999992_unfiltered.rds",
            "single_cell_metadata.tsv",
        ]
        OUTPUT_FILE_NAME = Sample.get_output_file_name(SAMPLE_ID, DOWNLOAD_CONFIG)
        SAMPLE_ZIP_PATH = common.OUTPUT_DATA_PATH / OUTPUT_FILE_NAME
        VALUES = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": OUTPUT_FILE_NAME,
            "size_in_bytes": 7145,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
