from django.conf import settings

from scpca_portal.enums import FileFormats, Modalities


class Project_SCPCP999990:
    SCPCA_ID = "SCPCP999990"
    VALUES = {
        "abstract": "Abstract1",
        "additional_restrictions": "Research or academic purposes only",
        "diagnoses": ["diagnosis1", "diagnosis2", "diagnosis5"],
        "diagnoses_counts": {"diagnosis1": 1, "diagnosis2": 1, "diagnosis5": 2},
        "disease_timings": ["Initial diagnosis"],
        # This value is not determined until after computed file generation, and should be 3
        "downloadable_sample_count": 0,
        "has_bulk_rna_seq": True,
        "has_cite_seq_data": False,
        "has_multiplexed_data": False,
        "has_single_cell_data": True,
        "has_spatial_data": True,
        "human_readable_pi_name": "PI1",
        "includes_anndata": True,
        "includes_cell_lines": False,
        "includes_merged_sce": True,
        "includes_merged_anndata": True,
        "includes_xenografts": False,
        "modalities": [
            Modalities.SINGLE_CELL,
            Modalities.BULK_RNA_SEQ,
            Modalities.SPATIAL,
        ],
        "multiplexed_sample_count": 0,
        "organisms": ["Homo sapiens"],
        "original_file_paths": [
            "SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv",
            "SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv",
            "SCPCP999990/merged/SCPCP999990_merged-summary-report.html",
            "SCPCP999990/merged/SCPCP999990_merged.rds",
            "SCPCP999990/merged/SCPCP999990_merged_rna.h5ad",
        ],
        "pi_name": "scpca",
        "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
        "sample_count": 4,
        "scpca_id": SCPCA_ID,
        "seq_units": ["cell", "spot"],
        "technologies": ["10Xv3", "visium"],
        "title": "Title1",
        "unavailable_samples_count": 1,
    }

    class Sample_SCPCS999990:
        SCPCA_ID = "SCPCS999990"
        VALUES = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis1",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 3424,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["cell"],
            "subdiagnosis": "NA",
            "technologies": ["10Xv3"],
            "tissue_location": "tissue1",
            "treatment": "",
        }

    class Sample_SCPCS999991:
        SCPCA_ID = "SCPCS999991"
        VALUES = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis2",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": False,
            "has_spatial_data": True,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 0,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["spot"],
            "subdiagnosis": "NA",
            "technologies": ["visium"],
            "tissue_location": "tissue2",
            "treatment": "",
        }

    class Sample_SCPCS999994:
        SCPCA_ID = "SCPCS999994"
        VALUES = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis5",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": False,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 0,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["bulk"],
            "subdiagnosis": "NA",
            "technologies": ["paired_end"],
            "tissue_location": "tissue5",
            "treatment": "",
        }

    class Sample_SCPCS999997:
        SCPCA_ID = "SCPCS999997"
        VALUES = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis5",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 1570,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["cell"],
            "subdiagnosis": "NA",
            "technologies": ["10Xv3"],
            "tissue_location": "tissue8",
            "treatment": "",
        }

    class Library_SCPCL999990:
        SCPCA_ID = "SCPCL999990"
        VALUES = {
            "formats": [
                FileFormats.ANN_DATA,
                FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html",
                "SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad",
                "SCPCP999990/SCPCS999990/SCPCL999990_processed.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_processed_rna.h5ad",
                "SCPCP999990/SCPCS999990/SCPCL999990_qc.html",
                "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered_rna.h5ad",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Library_SCPCL999991:
        SCPCA_ID = "SCPCL999991"
        VALUES = {
            "formats": [
                FileFormats.SPATIAL_SPACERANGER,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SPATIAL,
            "original_file_paths": [
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Library_SCPCL999994:
        SCPCA_ID = "SCPCL999994"
        VALUES = {
            "formats": [],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.BULK_RNA_SEQ,
            "original_file_paths": [],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Library_SCPCL999997:
        SCPCA_ID = "SCPCL999997"
        VALUES = {
            "formats": [
                FileFormats.ANN_DATA,
                FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html",
                "SCPCP999990/SCPCS999997/SCPCL999997_filtered.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_filtered_rna.h5ad",
                "SCPCP999990/SCPCS999997/SCPCL999997_processed.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_processed_rna.h5ad",
                "SCPCP999990/SCPCS999997/SCPCL999997_qc.html",
                "SCPCP999990/SCPCS999997/SCPCL999997_unfiltered.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_unfiltered_rna.h5ad",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Summary1:
        VALUES = {
            "diagnosis": "diagnosis1",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }

    class Summary2:
        VALUES = {
            "diagnosis": "diagnosis2",
            "sample_count": 1,
            "seq_unit": "spot",
            "technology": "visium",
        }

    class Summary3:
        VALUES = {
            "diagnosis": "diagnosis5",
            "sample_count": 1,
            "seq_unit": "bulk",
            "technology": "paired_end",
        }

    class Summary4:
        VALUES = {
            "diagnosis": "diagnosis5",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }

    class Contact1:
        EMAIL = "{email contact 1}"
        VALUES = {
            "name": "{contact 1}",
            "email": EMAIL,
            "pi_name": "scpca",
        }

    class Contact2:
        EMAIL = "{email contact 2}"
        VALUES = {
            "name": "{contact 2}",
            "email": EMAIL,
            "pi_name": "scpca",
        }

    class ExternalAccession1:
        ACCESSION = "{SRA project accession}"
        VALUES = {
            "accession": ACCESSION,
            "has_raw": True,
            "url": "{SRA Run Selector URL}",
        }

    class ExternalAccession2:
        ACCESSION = "{GEO series accession}"
        VALUES = {
            "accession": ACCESSION,
            "has_raw": False,
            "url": "{GEO Series URL}",
        }

    class Publication1:
        DOI = "{doi 1}"
        VALUES = {
            "doi": DOI,
            "citation": "{formatted citation 1}",
            "pi_name": "scpca",
        }

    class Publication2:
        DOI = "{doi 2}"
        VALUES = {
            "doi": DOI,
            "citation": "{formatted citation 2}",
            "pi_name": "scpca",
        }
