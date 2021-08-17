import os

# Having to do this kinda seems to defeat the purpose of this pattern,
# but at least it's contained to this init file.
DJANGO_CONFIGURATION = os.environ.get("DJANGO_CONFIGURATION", "Local")
if DJANGO_CONFIGURATION == "Local":
    from scpca_portal.config.local import Local  # noqa
elif DJANGO_CONFIGURATION == "Production":
    from scpca_portal.config.production import Production  # noqa
