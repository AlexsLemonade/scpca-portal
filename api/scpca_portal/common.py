from pathlib import Path

from django.conf import settings

# Locally the docker container puts the code in a folder called code.
# This allows us to run the same command on production or locally.
CODE_PATH = (
    code_path
    if (code_path := Path("/home/user/code")) and code_path.exists()
    else Path("/home/user")
)

CSV_MULTI_VALUE_DELIMITER = ";"

DATA_PATH = CODE_PATH / ("test_data" if settings.TEST else "data")
INPUT_DATA_PATH = DATA_PATH / "input"
OUTPUT_DATA_PATH = DATA_PATH / "output"

TEMPLATE_PATH = CODE_PATH / "scpca_portal" / "templates"

TEST_INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs/2024-06-28/"
INPUT_BUCKET_NAME = TEST_INPUT_BUCKET_NAME if settings.TEST else "scpca-portal-inputs"

TAB = "\t"
NA = "NA"  # "Not Available"

IGNORED_INPUT_VALUES = {"", "N/A", "TBD"}
STRIPPED_INPUT_VALUES = "< >"

# Formats
ANN_DATA = "ANN_DATA"
SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"

FORMAT_EXTENSIONS = {ANN_DATA: ".h5ad", SINGLE_CELL_EXPERIMENT: ".rds"}

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
    "age_at_diagnosis",
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
    "sample_cell_count_estimate",
    "sample_cell_estimate",  # ONLY FOR MULTIPLEXED
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

GENERATED_PROJECT_DOWNLOAD_CONFIG = [
    # SINGLE CELL SCE CONFIGURATIONS
    {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": False,
    },
    {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    # Notes about merged objects (accoring to scpca portal documentation):
    #   Only Single-cell (not spatial) for sce and anndata
    #   Only projects with non-multiplexed libraries can be merged
    #   Merged objects are unavailable for projects with > 100 samples
    {
        "modality": "SINGLE_CELL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    # SINGLE CELL ANN DATA CONFIGURATIONS
    {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    {
        "modality": "SINGLE_CELL",
        "format": "ANN_DATA",
        "excludes_multiplexed": True,
        "includes_merged": True,
        "metadata_only": False,
    },
    # SPATIAL SCE CONFIGURATIONS
    {
        "modality": "SPATIAL",
        "format": "SINGLE_CELL_EXPERIMENT",
        "excludes_multiplexed": True,
        "includes_merged": False,
        "metadata_only": False,
    },
    # METADATA ONLY DOWNLOADS
    {
        "modality": None,
        "format": None,
        "excludes_multiplexed": False,
        "includes_merged": False,
        "metadata_only": True,
    },
]

GENERATED_SAMPLE_DOWNLOAD_CONFIGS = [
    {"modality": "SINGLE_CELL", "format": "SINGLE_CELL_EXPERIMENT"},
    {"modality": "SINGLE_CELL", "format": "ANN_DATA"},
    {"modality": "SPATIAL", "format": "SINGLE_CELL_EXPERIMENT"},
]

GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG = {
    "modality": None,
    "format": None,
    "excludes_multiplexed": False,
    "includes_merged": False,
    "metadata_only": True,
    "portal_metadata_only": True,
}


PORTAL_METADATA_COMPUTED_FILE_NAME = "portal_metadata.zip"
OUTPUT_PORTAL_METADATA_ZIP_FILE_PATH = OUTPUT_DATA_PATH / PORTAL_METADATA_COMPUTED_FILE_NAME
