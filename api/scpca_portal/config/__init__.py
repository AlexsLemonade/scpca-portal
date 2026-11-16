import os

DJANGO_CONFIGURATION = os.environ.get("DJANGO_CONFIGURATION", "Local")

if DJANGO_CONFIGURATION == "Test":
    from scpca_portal.config.test import Test  # noqa
elif DJANGO_CONFIGURATION == "Local":
    from scpca_portal.config.local import Local  # noqa
elif DJANGO_CONFIGURATION == "Staging":
    from scpca_portal.config.staging import Staging  # noqa
elif DJANGO_CONFIGURATION == "Dev":
    from scpca_portal.config.dev import Dev  # noqa
elif DJANGO_CONFIGURATION == "Production":
    from scpca_portal.config.production import Production  # noqa
