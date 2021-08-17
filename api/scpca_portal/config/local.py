import os
import sys

from scpca_portal.config.common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # AWS
    AWS_REGION = None

    # AWS Simple Email Service
    AWS_SES_DOMAIN = None

    # AWS S3
    AWS_S3_BUCKET_NAME = None

    # Local handling of uploaded files.
    TESTING = "test" in sys.argv

    if TESTING:
        LOCAL_FILE_DIRECTORY = "/home/user/code/test_uploaded_files"
    else:
        LOCAL_FILE_DIRECTORY = "/home/user/code/uploaded_files"

    if not os.path.exists(LOCAL_FILE_DIRECTORY):
        os.mkdir(LOCAL_FILE_DIRECTORY)

    # OAuth
    OAUTH_URL = "https://sandbox.orcid.org/oauth/token"

    CSRF_TRUSTED_ORIGINS = ["localhost", "127.0.0.1"]

    # This is only needed locally because everything else will use S3.
    DEV_HOST = os.getenv("DEV_HOST")
