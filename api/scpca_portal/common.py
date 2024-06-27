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

TAB = "\t"

IGNORED_INPUT_VALUES = {"", "N/A", "TBD"}
STRIPPED_INPUT_VALUES = "< >"

NA = "NA"  # A substitute for a "" or None field value in metadata
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
    "submitter",
    "submitter_id",
    "organism",
    "development_stage_ontology_term_id",
    "sex_ontology_term_id",
    "organism_ontology_id",
    "self_reported_ethnicity_ontology_term_id",
    "disease_ontology_term_id",
    "tissue_ontology_term_id",
    "*",  # Addtional metadata
    # Library metadata
    "seq_unit",
    "technology",
    "demux_samples",
    "total_reads",
    "mapped_reads",
    "sample_cell_count_estimate",
    "sample_cell_estimates",  # ONLY FOR MULTIPLEXED
    "unfiltered_cells",
    "filtered_cell_count",
    "processed_cells",
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
