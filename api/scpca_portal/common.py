import os

from django.conf import settings

# Locally the docker container puts the code in a folder called code.
# This allows us to run the same command on production or locally.
CODE_DIR = "/home/user/code/" if os.path.exists("/home/user/code") else "/home/user/"

DATA_DIR = os.path.join(CODE_DIR, "test_data" if settings.TEST else "data")
INPUT_DATA_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output")

TEMPLATE_DIR = os.path.join(CODE_DIR, "scpca_portal", "templates")

TAB = "\t"
