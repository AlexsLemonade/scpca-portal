import os

from scpca_portal.config.production import Production


class Staging(Production):
    """
    Settings for the staging deploy.
    Staging-only settings, such as restricted access to unreleased data, belong here.
    """

    # AWS S3
    AWS_S3_INPUT_BUCKET_NAME = os.getenv(
        "AWS_S3_INPUT_BUCKET_NAME", "scpca-portal-inputs-deployer-staging"
    )
