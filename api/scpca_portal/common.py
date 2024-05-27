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

# Global sort order for the field names in Metadata TSVs
METADATA_SORT_ORDER = [
    # sample metadata
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
    # library metadata
    "seq_unit",
    "technology",
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
    # project metadata
    "scpca_project_id",
    "pi_name",
    "project_title",
    # processing metadata
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
