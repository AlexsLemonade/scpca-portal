from scpca_portal.config.production import Production


class Dev(Production):
    """
    Settings for deployed dev stacks.
    """

    # AWS S3
    # TODO: update this when we decide what to do with the dev input bucket
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-input"
