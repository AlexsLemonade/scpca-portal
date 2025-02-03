from django.conf import settings

from scpca_portal.models import Library, Sample


class Project_SCPCP999992:
    SCPCA_ID = "SCPCP999992"
    VALUES = {
        "abstract": "TBD",
        "additional_restrictions": "Research or academic purposes only",
        "diagnoses": "diagnosis7",
        "diagnoses_counts": "diagnosis7 (2)",
        "disease_timings": "Initial diagnosis",
        # This value is not determined until after computed file generation, and should be 2
        "downloadable_sample_count": 0,
        "has_bulk_rna_seq": False,
        "has_cite_seq_data": True,
        "has_multiplexed_data": False,
        "has_single_cell_data": True,
        "has_spatial_data": False,
        "human_readable_pi_name": "TBD",
        "includes_anndata": True,
        "includes_cell_lines": False,
        "includes_merged_sce": True,
        "includes_merged_anndata": True,
        "includes_xenografts": False,
        "modalities": [Sample.Modalities.NAME_MAPPING[Sample.Modalities.CITE_SEQ]],
        "multiplexed_sample_count": 0,
        "organisms": ["Homo sapiens"],
        "original_file_paths": [
            "SCPCP999992/merged/SCPCP999992_merged-summary-report.html",
            "SCPCP999992/merged/SCPCP999992_merged.rds",
            "SCPCP999992/merged/SCPCP999992_merged_adt.h5ad",
            "SCPCP999992/merged/SCPCP999992_merged_rna.h5ad",
        ],
        "pi_name": "scpca",
        "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
        "sample_count": 2,
        "scpca_id": SCPCA_ID,
        "seq_units": "cell",
        "technologies": "10Xv2_5prime, 10Xv3",
        "title": "TBD",
        "unavailable_samples_count": 0,
    }

    class Sample_SCPCS999996:
        SCPCA_ID = "SCPCS999996"
        VALUES = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis7",
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
            "sample_cell_count_estimate": 3425,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv3",
            "tissue_location": "tissue7",
            "treatment": "",
        }

    class Sample_SCPCS999998:
        SCPCA_ID = "SCPCS999998"
        VALUES = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate_sum": None,
            "diagnosis": "diagnosis7",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": True,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 5247,
            "scpca_id": SCPCA_ID,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv2_5prime",
            "tissue_location": "tissue9",
            "treatment": "",
        }

    class Library_SCPCL999996:
        SCPCA_ID = "SCPCL999996"
        VALUES = {
            "data_file_paths": [
                "SCPCP999992/SCPCS999996/SCPCL999996_celltype-report.html",
                "SCPCP999992/SCPCS999996/SCPCL999996_filtered.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_filtered_rna.h5ad",
                "SCPCP999992/SCPCS999996/SCPCL999996_processed.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_processed_rna.h5ad",
                "SCPCP999992/SCPCS999996/SCPCL999996_qc.html",
                "SCPCP999992/SCPCS999996/SCPCL999996_unfiltered.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_unfiltered_rna.h5ad",
            ],
            "formats": [
                Library.FileFormats.ANN_DATA,
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": SCPCA_ID,
            "workflow_version": "development",
        }

    class Library_SCPCL999998:
        SCPCA_ID = "SCPCL999998"
        VALUES = {
            "data_file_paths": [
                "SCPCP999992/SCPCS999998/SCPCL999998_celltype-report.html",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered_rna.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed_rna.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_qc.html",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered_rna.h5ad",
            ],
            "formats": [
                Library.FileFormats.ANN_DATA,
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": True,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": SCPCA_ID,
            "workflow_version": "development",
        }

    class Summary1:
        VALUES = {
            "diagnosis": "diagnosis7",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }

    class Summary2:
        VALUES = {
            "diagnosis": "diagnosis7",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv2_5prime",
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
