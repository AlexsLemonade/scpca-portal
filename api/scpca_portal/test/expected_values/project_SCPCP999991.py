from django.conf import settings

from scpca_portal.enums import FileFormats, Modalities


class Project_SCPCP999991:
    SCPCA_ID = "SCPCP999991"
    VALUES = {
        "abstract": "Abstract2",
        "additional_restrictions": "Research or academic purposes only",
        "diagnoses": ["diagnosis3", "diagnosis4", "diagnosis6"],
        "diagnoses_counts": {"diagnosis3": 1, "diagnosis4": 1, "diagnosis6": 1},
        "disease_timings": ["Initial diagnosis"],
        # This value is not determined until after computed file generation, and should be 2
        "downloadable_sample_count": 0,
        "has_bulk_rna_seq": False,
        "has_cite_seq_data": False,
        "has_multiplexed_data": True,
        "has_single_cell_data": True,
        "has_spatial_data": False,
        "human_readable_pi_name": "PI2",
        "includes_anndata": True,
        "includes_cell_lines": False,
        "includes_merged_sce": False,
        "includes_merged_anndata": False,
        "includes_xenografts": False,
        "modalities": [
            Modalities.SINGLE_CELL,
            Modalities.MULTIPLEXED,
        ],
        "multiplexed_sample_count": 2,
        "organisms": ["Homo sapiens"],
        "original_file_paths": [],
        "pi_name": "scpca",
        "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
        "sample_count": 3,
        "scpca_id": SCPCA_ID,
        "seq_units": ["cell", "nucleus"],
        "technologies": ["10Xv3", "10Xv3.1"],
        "title": "Title2",
        "unavailable_samples_count": 0,
    }

    class Sample_SCPCS999992:
        SCPCA_ID = "SCPCS999992"
        VALUES = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate_sum": 100,
            "diagnosis": "diagnosis4",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": ["SCPCS999993"],
            "sample_cell_count_estimate": None,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["nucleus"],
            "subdiagnosis": "NA",
            "technologies": ["10Xv3.1"],
            "tissue_location": "tissue3",
            "treatment": "",
        }

    class Sample_SCPCS999993:
        SCPCA_ID = "SCPCS999993"
        VALUES = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate_sum": 110,
            "diagnosis": "diagnosis3",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": ["SCPCS999992"],
            "sample_cell_count_estimate": None,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["nucleus"],
            "subdiagnosis": "NA",
            "technologies": ["10Xv3.1"],
            "tissue_location": "tissue4",
            "treatment": "",
        }

    class Sample_SCPCS999995:
        SCPCA_ID = "SCPCS999995"
        VALUES = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis6",
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
            "sample_cell_count_estimate": 3419,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": ["cell"],
            "subdiagnosis": "NA",
            "technologies": ["10Xv3"],
            "tissue_location": "tissue6",
            "treatment": "",
        }

    class Library_SCPCL999992:
        SCPCA_ID = "SCPCL999992"
        VALUES = {
            "formats": [
                FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": True,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_celltype-report.html",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_filtered.rds",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_processed.rds",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_qc.html",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_unfiltered.rds",
            ],
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Library_SCPCL999995:
        SCPCA_ID = "SCPCL999995"
        VALUES = {
            "formats": [FileFormats.ANN_DATA, FileFormats.SINGLE_CELL_EXPERIMENT],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Modalities.SINGLE_CELL,
            "original_file_paths": [
                "SCPCP999991/SCPCS999995/SCPCL999995_celltype-report.html",
                "SCPCP999991/SCPCS999995/SCPCL999995_filtered.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_filtered_rna.h5ad",
                "SCPCP999991/SCPCS999995/SCPCL999995_processed.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_processed_rna.h5ad",
                "SCPCP999991/SCPCS999995/SCPCL999995_qc.html",
                "SCPCP999991/SCPCS999995/SCPCL999995_unfiltered.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_unfiltered_rna.h5ad",
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "scpca_id": SCPCA_ID,
            "workflow_version": "v0.8.8",
        }

    class Summary1:
        VALUES = {
            "diagnosis": "diagnosis4",
            "sample_count": 1,
            "seq_unit": "nucleus",
            "technology": "10Xv3.1",
        }

    class Summary2:
        VALUES = {
            "diagnosis": "diagnosis3",
            "sample_count": 1,
            "seq_unit": "nucleus",
            "technology": "10Xv3.1",
        }

    class Summary3:
        VALUES = {
            "diagnosis": "diagnosis6",
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
