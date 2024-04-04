import logging
from argparse import BooleanOptionalAction
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.models import Project
from scpca_portal.services.loader.loader import Loader

ALLOWED_SUBMITTERS = {
    "christensen",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "mullighan",
    "murphy_chen",
    "pugh",
    "teachey_tan",
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class Command(BaseCommand):
    help = """Populates the database with data.

    The data should be contained in an S3 bucket called scpca-portal-inputs.

    The directory structure for this bucket should follow this pattern:
        /project_metadata.csv
        /SCPCP000001/libraries_metadata.csv
        /SCPCP000001/samples_metadata.csv
        /SCPCP000001/SCPCS000109/SCPCL000126_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000126_processed.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000126_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000127_processed.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000127_unfiltered.rds

    The files will be zipped up and stats will be calculated for them.

    If run locally the zipped ComputedFiles will be copied to the
    "scpca-local-data" bucket.

    If run in the cloud the zipped ComputedFiles files will be copied
    to a stack-specific S3 bucket."""

    def add_arguments(self, parser):
        parser.add_argument("--input-bucket-name", type=str, default="scpca-portal-inputs")
        parser.add_argument(
            "--clean-up-input-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )
        parser.add_argument(
            "--clean-up-output-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )
        parser.add_argument("--max-workers", type=int, default=10)
        parser.add_argument("--reload-all", action="store_true")
        parser.add_argument("--reload-existing", action="store_true")
        parser.add_argument("--s3-max-bandwidth", type=int, default=None, help="In MB/s")
        parser.add_argument("--s3-max-concurrent-requests", type=int, default=10)
        parser.add_argument("--s3-multipart-chunk-size", type=int, default=8, help="In MB")
        parser.add_argument("--scpca-project-id", type=str)
        parser.add_argument("--scpca-sample-id", type=str)
        parser.add_argument("--skip-sync", action="store_true", default=False)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, default=settings.UPDATE_S3_DATA
        )

    def handle(self, *args, **kwargs):
        Loader.load_data(**kwargs)