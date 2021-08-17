"""
WSGI config for scpca_portal project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import os

from configurations.wsgi import get_wsgi_application  # noqa

# Needs to be above import because importing get_wsgi_application will
# look for this environment variable.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scpca_portal.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")



application = get_wsgi_application()
