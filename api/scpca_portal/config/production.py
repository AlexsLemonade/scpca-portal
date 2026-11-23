from scpca_portal.config.cloud import Cloud


class Production(Cloud):
    """Settings for the production deploy.

    Shared deploy settings live in Cloud.
    Settings are overriden here that are specific to production.
    """
