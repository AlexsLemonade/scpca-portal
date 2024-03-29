import os

from scpca_portal.config.common import Common


class Local(Common):
    DEBUG = True

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    UPDATE_S3_DATA = False

    # AWS.
    AWS_REGION = None

    # AWS S3 hardcoded to a bucket used for local dev.
    AWS_S3_BUCKET_NAME = "scpca-local-data"

    CSRF_TRUSTED_ORIGINS = ["localhost", "127.0.0.1"]

    # This is only needed locally because everything else will use S3.
    DEV_HOST = os.getenv("DEV_HOST")
