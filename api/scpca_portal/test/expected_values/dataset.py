from django.conf import settings

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities


class Dataset:
    class AllMetadata:
        CCDL_NAME = CCDLDatasetNames.ALL_METADATA.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: ["SCPCS999991"],
                },
                "SCPCP999991": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.METADATA.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class AllMetadataSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SingleCellSingleCellExperiment:
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999991": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class SingleCellSingleCellExperimentSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SingleCellSingleCellExperimentNoMultiplexedSCPCP999991:
        PROJECT_ID = "SCPCP999991"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SingleCellSingleCellExperimentMerged:
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999991": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class SingleCellSingleCellExperimentMergedSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SingleCellAnndata:
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999991": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.ANN_DATA.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class SingleCellAnndataSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.ANN_DATA.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SingleCellAnndataMerged:
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999991": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999995"],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.ANN_DATA.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class SingleCellAnndataMergedSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": True,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL.value: [],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.ANN_DATA.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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

    class SpatialSingleCellExperiment:
        CCDL_NAME = CCDLDatasetNames.SPATIAL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                "SCPCP999990": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: [],
                    Modalities.SPATIAL.value: ["SCPCS999991"],
                },
                "SCPCP999991": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: [],
                    Modalities.SPATIAL.value: [],
                },
                "SCPCP999992": {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: [],
                    Modalities.SPATIAL.value: [],
                },
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
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

    class SpatialSingleCellExperimentSCPCP999990:
        PROJECT_ID = "SCPCP999990"
        CCDL_NAME = CCDLDatasetNames.SPATIAL_SINGLE_CELL_EXPERIMENT.value
        VALUES = {
            "data": {
                PROJECT_ID: {
                    "merge_single_cell": False,
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL.value: [],
                    Modalities.SPATIAL.value: ["SCPCS999991"],
                }
            },
            "email": None,
            "start": False,
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT.value,
            "regenerated_from": None,
            "is_ccdl": True,
            "ccdl_name": CCDL_NAME,
            "ccdl_project_id": PROJECT_ID,
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
