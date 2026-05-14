"""
This custom plugin gives mypy_django_plugin an entry point to django-configurations
in order to load Django settings modules (which are organized as classes and inherit from it).
This django-configurations entrypoint is similar to how its done in manage.py and wsgi.py.
"""

import os

from configurations.importer import install
from mypy_django_plugin import main

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scpca_portal.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
install()

plugin = main.plugin
