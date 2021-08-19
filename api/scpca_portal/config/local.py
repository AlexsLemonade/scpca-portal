import os

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

    # AWS S3
    AWS_S3_BUCKET_NAME = None

    CSRF_TRUSTED_ORIGINS = ["localhost", "127.0.0.1"]

    # This is only needed locally because everything else will use S3.
    DEV_HOST = os.getenv("DEV_HOST")
