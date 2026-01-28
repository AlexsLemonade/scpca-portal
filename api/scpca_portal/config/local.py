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
    AWS_REGION = "us-east-1"

    # AWS S3
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-inputs"
    AWS_S3_OUTPUT_BUCKET_NAME = "scpca-local-data"

    CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]

    # This is only needed locally because everything else will use S3.
    DEV_HOST = os.getenv("DEV_HOST")

    # Code Paths
    INPUT_DATA_PATH = Path("/home/user/code/data/input")
    OUTPUT_DATA_PATH = Path("/home/user/code/data/output")
    README_PATH = Path("/home/user/code/data/readmes")
    TEMPLATE_PATH = Path("/home/user/code/scpca_portal/templates")
