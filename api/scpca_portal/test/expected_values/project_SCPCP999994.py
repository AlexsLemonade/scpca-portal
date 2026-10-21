from django.conf import settings

from scpca_portal.enums import FileFormats, Modalities

# This project contains GEM-X Flex libraries with compound IDs in the format SCPCLXXXXXX-SCPCSXXXXXX


class Project_SCPCP999994:
    SCPCA_ID = "SCPCP999994"
    VALUES = {
        "abstract": "Abstract5",
        "additional_restrictions": "Research or academic purposes only",
        "diagnoses": ["diagnosis9"],
        "diagnoses_counts": {"diagnosis8": 2},
        "disease_timings": ["Initial diagnosis"],
        "downloadable_sample_count": 2,
        "has_bulk_rna_seq": False,
        "has_cite_seq_data": False,
        "has_multiplexed_data": False,
        "has_single_cell_data": True,
        "has_spatial_data": False,
        "human_readable_pi_name": "PI5",
        "includes_anndata": True,
        "includes_cell_lines": False,
        "includes_merged_sce": True,
        "includes_merged_anndata": True,
        "includes_xenografts": False,
        "is_locked": False,
        "modalities": [Modalities.SINGLE_CELL],
        "multiplexed_sample_count": 0,
        "organisms": ["Homo sapiens"],
        "pi_name": "scpca",
        "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
        "sample_count": 2,
        "scpca_id": SCPCA_ID,
        "seq_units": ["nucleus-FFPE"],
        "technologies": ["10xflex_v1.1_multi"],
        "title": "Title5",
        "unavailable_samples_count": 0,
    }

    class Sample_SCPCS999988:
        SCPCA_ID = "SCPCS999988"
        VALUES = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis8",
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
            "sample_cell_count_estimate": 674,
            "scpca_id": SCPCA_ID,
            "seq_units": ["nucleus-FFPE"],
            "sex": "M",
            "subdiagnosis": "NA",
            "technologies": ["10xflex_v1.1_multi"],
            "tissue_location": "tissue10",
            "treatment": "",
        }

    class Sample_SCPCS999989:
        SCPCA_ID = "SCPCS999989"
        VALUES = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis8",
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
            "sample_cell_count_estimate": 934,
            "scpca_id": SCPCA_ID,
            "seq_units": ["nucleus-FFPE"],
            "sex": "M",
            "subdiagnosis": "NA",
            "technologies": ["10xflex_v1.1_multi"],
            "tissue_location": "tissue11",
            "treatment": "",
        }

    class Library_SCPCL999989_SCPCS999988:
        SCPCA_ID = "SCPCL999989-SCPCS999988"
        VALUES = {
            "formats": [
                FileFormats.ANN_DATA,
                FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_celltype-report.html",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_filtered.rds",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_filtered_rna.h5ad",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_processed.rds",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_processed_rna.h5ad",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_qc.html",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_unfiltered.rds",
                "SCPCP999994/SCPCS999988/SCPCL999989-SCPCS999988_unfiltered_rna.h5ad",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.10.4",
        }

    class Library_SCPCL999989_SCPCS999989:
        SCPCA_ID = "SCPCL999989-SCPCS999989"
        VALUES = {
            "formats": [
                FileFormats.ANN_DATA,
                FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_celltype-report.html",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_filtered.rds",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_filtered_rna.h5ad",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_processed.rds",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_processed_rna.h5ad",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_qc.html",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_unfiltered.rds",
                "SCPCP999994/SCPCS999989/SCPCL999989-SCPCS999989_unfiltered_rna.h5ad",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.10.4",
        }

    class Summary:
        VALUES = {
            "diagnosis": "diagnosis8",
            "sample_count": 2,
            "seq_unit": "nucleus-FFPE",
            "technology": "10xflex_v1.1_multi",
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
