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
INPUT_MERGED_DATA_PATH = INPUT_DATA_PATH / "merged"
OUTPUT_DATA_PATH = DATA_PATH / "output"

TEMPLATE_PATH = CODE_PATH / "scpca_portal" / "templates"

TAB = "\t"
