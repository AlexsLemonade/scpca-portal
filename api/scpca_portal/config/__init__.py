import os

DJANGO_CONFIGURATION = os.environ.get("DJANGO_CONFIGURATION", "Local")
if DJANGO_CONFIGURATION == "Local":
    from scpca_portal.config.local import Local  # noqa
elif DJANGO_CONFIGURATION == "Production":
    from scpca_portal.config.production import Production  # noqa
