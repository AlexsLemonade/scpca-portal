import os

from django.conf import settings

# Locally the docker container puts the code in a folder called code.
# This allows us to run the same command on production or locally.
CODE_DIR = "/home/user/code/" if os.path.exists("/home/user/code") else "/home/user/"

DATA_DIR_NAME = "data"
TEST_DATA_DIR_NAME = "test_data"
DATA_DIR = os.path.join(CODE_DIR, TEST_DATA_DIR_NAME if settings.TEST else DATA_DIR_NAME)
TEMPLATE_DIR = os.path.join(CODE_DIR, "scpca_portal", "templates")

INPUT_DATA_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output")
README_FILE_NAME = "README.md"
README_FILE_PATH = os.path.join(OUTPUT_DATA_DIR, README_FILE_NAME)
README_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "readme.md")

TAB = "\t"
