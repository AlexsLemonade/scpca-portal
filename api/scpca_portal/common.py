from scpca_portal.enums import JobStates, Modalities

CSV_MULTI_VALUE_DELIMITER = ";"

TAB = "\t"
NA = "NA"  # "Not Available"

GB_IN_BYTES = 1000000000

IGNORED_INPUT_VALUES = {"", NA, "TBD"}
STRIPPED_INPUT_VALUES = "< >"

# Formats
ANN_DATA = "ANN_DATA"
SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

FORMAT_EXTENSIONS = {ANN_DATA: ".h5ad", SINGLE_CELL_EXPERIMENT: ".rds"}
SUPPLEMENTARY_EXTENSIONS = {".html"}
OUTPUT_METADATA_EXTENSION = ".tsv"
CITE_SEQ_FILENAME_ENDING = f"_adt{FORMAT_EXTENSIONS[ANN_DATA]}"

BULK_INPUT_DIR = "bulk"
MERGED_INPUT_DIR = "merged"
MERGED_REPORTS_PREFEX_DIR = "individual_reports"

MULTIPLEXED_SAMPLES_INPUT_DELIMETER = ","
MULTIPLEXED_SAMPLES_OUTPUT_DELIMETER = "_"

SUBMITTER_WHITELIST = {
    "christensen",
    "collins",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "mullighan",
    "murphy_chen",
    "pugh",
    "teachey_tan",
    "wu",
    "rokita",
    "soragni",
    "pushel",
}

# Modalities default sort order
MODALITIES_DEFAULT_SORT_ORDER = [
    Modalities.SINGLE_CELL,
    Modalities.BULK_RNA_SEQ,
    Modalities.CITE_SEQ,
    Modalities.MULTIPLEXED,
    Modalities.SPATIAL,
]

# Global sort order for Metadata TSVs
# Columns
METADATA_COLUMN_SORT_ORDER = [
    "scpca_project_id",
    # Sample metadata
    "scpca_sample_id",
    "scpca_library_id",
    "diagnosis",
    "subdiagnosis",
    "disease_timing",
    "age",
    "age_timing",
    "sex",
    "tissue_location",
    "participant_id",
    "submitter_id",
    "organism",
    "development_stage_ontology_term_id",
    "sex_ontology_term_id",
    "organism_ontology_id",
    "self_reported_ethnicity_ontology_term_id",
    "disease_ontology_term_id",
    "tissue_ontology_term_id",
    "*",  # Any metadata key not explicitly enumerated in the sort order is inserted here
    # Library metadata
    "seq_unit",
    "technology",
    "demux_samples",
    "total_reads",
    "mapped_reads",
    "demux_cell_count_estimate",  # ONLY FOR MULTIPLEXED
    "unfiltered_cells",
    "filtered_cell_count",
    "processed_cells",
    "filtered_spots",  # SPATIAL
    "unfiltered_spots",  # SPATIAL
    "tissue_spots",  # SPATIAL
    "has_cellhash",
    "includes_anndata",
    "is_cell_line",
    "is_multiplexed",
    "is_xenograft",
    # Project metadata
    "pi_name",
    "project_title",
    # Processing metadata
    "genome_assembly",
    "mapping_index",
    "spaceranger_version",  # FOR SPATIAL ONLY
    "alevin_fry_version",  # REMOVED FOR SPATIAL
    "salmon_version",  # REMOVED FOR SPATIAL
    "transcript_type",  # REMOVED FOR SPATIAL
    "droplet_filtering_method",  # REMOVED FOR SPATIAL
    "cell_filtering_method",  # REMOVED FOR SPATIAL
    "prob_compromised_cutoff",  # REMOVED FOR SPATIAL
    "min_gene_cutoff",  # REMOVED FOR SPATIAL
    "normalization_method",  # REMOVED FOR SPATIAL
    "demux_method",  # ONLY FOR MULTIPLEXED
    "date_processed",
    "workflow",
    "workflow_version",
    "workflow_commit",
]
# Rows
PROJECT_ID_KEY = "scpca_project_id"
SAMPLE_ID_KEY = "scpca_sample_id"
LIBRARY_ID_KEY = "scpca_library_id"

# Id Prefixes
PROJECT_ID_PREFIX = "SCPCP"
SAMPLE_ID_PREFIX = "SCPCS"
LIBRARY_ID_PREFIX = "SCPCL"

PROJECT_DOWNLOAD_CONFIGS = {
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": False,
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    "SINGLE_CELL_ANN_DATA": {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "SINGLE_CELL_ANN_DATA_MERGED": {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    "SPATIAL": {
        "modality": "SPATIAL",
        "format": "SPATIAL_SPACERANGER",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    "ALL_METADATA": {
        "modality": None,
        "format": None,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": True,
    },
}

SAMPLE_DOWNLOAD_CONFIGS = {
    "SINGLE_CELL_SINGLE_CELL_EXPERIMENT": {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
    },
    "SINGLE_CELL_ANN_DATA": {"modality": "SINGLE_CELL", "format": "ANN_DATA"},
    "SPATIAL": {"modality": "SPATIAL", "format": "SPATIAL_SPACERANGER"},
}

PORTAL_METADATA_DOWNLOAD_CONFIG = {
    "modality": None,
    "format": None,
    "excludes_multiplexed": False,
    "includes_merged": False,
    "metadata_only": True,
    "portal_metadata_only": True,
}

PORTAL_METADATA_COMPUTED_FILE_NAME = "PORTAL_ALL_METADATA.zip"

# Batch job
FINAL_JOB_STATES = [JobStates.SUCCEEDED, JobStates.FAILED, JobStates.TERMINATED]
SUBMITTED_JOB_STATES = [JobStates.PROCESSING, *FINAL_JOB_STATES]
MAX_JOB_ATTEMPTS = 5
