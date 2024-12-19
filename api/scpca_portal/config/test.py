from pathlib import Path

from scpca_portal.config.local import Local


class Test(Local):
    # AWS S3
    # Note: Data must be resynced when test bucket is updated
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs/2024-09-10"

    # Code Paths
    INPUT_DATA_PATH = Path("/home/user/code/test_data/input")
    OUTPUT_DATA_PATH = Path("/home/user/code/test_data/output")
    README_PATH = Path("/home/user/code/test_data/readmes")
    TEMPLATE_PATH = Path("/home/user/code/scpca_portal/templates")
    RENDERED_README_PATH = Path("/home/user/code/scpca_portal/test/expected_values/readmes")
