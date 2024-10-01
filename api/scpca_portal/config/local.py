import os
from pathlib import Path

from scpca_portal.config.common import Common


class Local(Common):
    DEBUG = True

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    UPDATE_S3_DATA = False

    # AWS
    AWS_REGION = None

    # AWS S3
    TEST_INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs/2024-09-10/"
    AWS_S3_INPUT_BUCKET_NAME = TEST_INPUT_BUCKET_NAME if Common.TEST else "scpca-portal-inputs"
    AWS_S3_OUTPUT_BUCKET_NAME = "scpca-local-data"

    CSRF_TRUSTED_ORIGINS = ["localhost", "127.0.0.1"]

    # This is only needed locally because everything else will use S3.
    DEV_HOST = os.getenv("DEV_HOST")

    # Code Paths
    CODE_PATH = Path("/home/user/code")

    DATA_PATH = CODE_PATH / ("test_data" if Common.TEST else "data")
    INPUT_DATA_PATH = DATA_PATH / "input"
    OUTPUT_DATA_PATH = DATA_PATH / "output"

    TEMPLATE_PATH = CODE_PATH / "scpca_portal" / "templates"
