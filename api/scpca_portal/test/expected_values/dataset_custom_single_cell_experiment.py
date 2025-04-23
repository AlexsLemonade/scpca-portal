from django.conf import settings

from scpca_portal.enums import DatasetFormats, Modalities


class DatasetCustomSingleCellExperiment:
    VALUES = {
        "data": {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "merge_single_cell": False,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "merge_single_cell": True,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        },
        "email": None,
        "start": False,
        "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
        "regenerated_from": None,
        "is_ccdl": False,
        "ccdl_name": None,
        "ccdl_project_id": None,
        "started_at": None,
        "is_started": False,
        "is_processing": False,
        "processed_at": None,
        "is_processed": False,
        "errored_at": None,
        "is_errored": False,
        "error_message": None,
        "expires_at": None,
        "is_expired": False,
    }
    COMPUTED_FILE_LIST = [
        "SCPCP999990_single_cell/SCPCS999990/SCPCL999990_celltype-report.html",
        "SCPCP999990_single_cell/SCPCS999990/SCPCL999990_filtered.rds",
        "SCPCP999990_single_cell/SCPCS999990/SCPCL999990_processed.rds",
        "SCPCP999990_single_cell/SCPCS999990/SCPCL999990_qc.html",
        "SCPCP999990_single_cell/SCPCS999990/SCPCL999990_unfiltered.rds",
        "SCPCP999990_single_cell/SCPCS999997/SCPCL999997_celltype-report.html",
        "SCPCP999990_single_cell/SCPCS999997/SCPCL999997_filtered.rds",
        "SCPCP999990_single_cell/SCPCS999997/SCPCL999997_processed.rds",
        "SCPCP999990_single_cell/SCPCS999997/SCPCL999997_qc.html",
        "SCPCP999990_single_cell/SCPCS999997/SCPCL999997_unfiltered.rds",
        "SCPCP999990_single-cell/single-cell_metadata.tsv",
        "SCPCP999990_bulk_rna/SCPCP999990_bulk_metadata.tsv",
        "SCPCP999990_bulk_rna/SCPCP999990_bulk_quant.tsv",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",  # noqa
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",  # noqa
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",  # noqa
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png",
        "SCPCP999990_spatial/SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv",
        "SCPCP999990_spatial/spatial_metadata.tsv",
        "SCPCP999991_single_cell/SCPCS999992_SCPCS999993/SCPCL999992_celltype-report.html",
        "SCPCP999991_single_cell/SCPCS999992_SCPCS999993/SCPCL999992_filtered.rds",
        "SCPCP999991_single_cell/SCPCS999992_SCPCS999993/SCPCL999992_processed.rds",
        "SCPCP999991_single_cell/SCPCS999992_SCPCS999993/SCPCL999992_qc.html",
        "SCPCP999991_single_cell/SCPCS999992_SCPCS999993/SCPCL999992_unfiltered.rds",
        "SCPCP999991_single_cell/SCPCS999995/SCPCL999995_celltype-report.html",
        "SCPCP999991_single_cell/SCPCS999995/SCPCL999995_filtered.rds",
        "SCPCP999991_single_cell/SCPCS999995/SCPCL999995_processed.rds",
        "SCPCP999991_single_cell/SCPCS999995/SCPCL999995_qc.html",
        "SCPCP999991_single_cell/SCPCS999995/SCPCL999995_unfiltered.rds",
        "SCPCP999991_single-cell/single-cell_metadata.tsv",
        "SCPCP999992_single-cell_merged/SCPCP999992_merged-summary-report.html",
        "SCPCP999992_single-cell_merged/SCPCP999992_merged.rds",
        "SCPCP999992_single-cell_merged/individual_reports/SCPCS999996/SCPCL999996_celltype-report.html",  # noqa
        "SCPCP999992_single-cell_merged/individual_reports/SCPCS999996/SCPCL999996_qc.html",
        "SCPCP999992_single-cell_merged/individual_reports/SCPCS999998/SCPCL999998_celltype-report.html",  # noqa
        "SCPCP999992_single-cell_merged/individual_reports/SCPCS999998/SCPCL999998_qc.html",
        "SCPCP999992_single-cell_merged/single-cell_metadata.tsv",
        "README.md",
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
        "size_in_bytes": 9113,
        "workflow_version": "development",
        "includes_celltype_report": True,
    }
