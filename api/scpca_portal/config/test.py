from pathlib import Path

from scpca_portal.config.local import Local


class Test(Local):
    # AWS S3
    # Data must be resynced when test bucket is updated
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs/2024-09-10/"
    AWS_S3_OUTPUT_BUCKET_NAME = "scpca-local-data"

    # Code Paths
    CODE_PATH = Path("/home/user/code")

    DATA_PATH = CODE_PATH / "test_data"
    INPUT_DATA_PATH = DATA_PATH / "input"
    OUTPUT_DATA_PATH = DATA_PATH / "output"

    TEMPLATE_PATH = CODE_PATH / "scpca_portal" / "templates"
