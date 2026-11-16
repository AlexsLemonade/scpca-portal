import os

from scpca_portal.config.production import Production


class Staging(Production):
    # AWS S3
    AWS_S3_INPUT_BUCKET_NAME = os.getenv(
        "AWS_S3_INPUT_BUCKET_NAME", "scpca-portal-inputs-deployer-staging"
    )
