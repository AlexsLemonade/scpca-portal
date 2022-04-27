import csv
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample

ALLOWED_SUBMITTERS = {
    "christensen",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "murphy_chen",
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


def cleanup_output_data_dir():
    cleanup_items = (ComputedFile.README_FILE_NAME, "*.tsv")
    for item in cleanup_items:
        for path in Path(common.OUTPUT_DATA_DIR).glob(item):
            path.unlink()


def load_data_from_s3(
    update_s3_data: bool,
    reload_all: bool,
    reload_existing: bool,
    scpca_project_ids=None,
    scpca_sample_ids=None,
    allowed_submitters=ALLOWED_SUBMITTERS,
    input_bucket_name="scpca-portal-inputs",
):
    """Loads data from S3. Creates projects and loads data for them."""

    if reload_all:
        logger.info("Purging all projects")
        for project in Project.objects.order_by("scpca_id"):
            project.purge(delete_from_s3=update_s3_data)

    # Prepare data input directory.
    if not os.path.exists(common.INPUT_DATA_DIR):
        os.makedirs(common.INPUT_DATA_DIR)

    # Prepare data output directory.
    shutil.rmtree(common.OUTPUT_DATA_DIR, ignore_errors=True)
    os.mkdir(common.OUTPUT_DATA_DIR)

    command_list = [
        "aws",
        "s3",
        "sync",
        "--delete",
        f"s3://{input_bucket_name}",
        common.INPUT_DATA_DIR,
    ]
    if "public-test" in input_bucket_name:
        command_list.append("--no-sign-request")
    subprocess.check_call(command_list)

    with open(Project.get_input_metadata_path()) as project_csv:
        project_list = list(csv.DictReader(project_csv))

    for project_data in project_list:
        scpca_id = project_data["scpca_project_id"]
        if scpca_project_ids and scpca_id not in scpca_project_ids:
            continue

        if project_data["submitter"] not in allowed_submitters:
            continue

        # Purge existing projects so they can be readded.
        if reload_existing:
            try:
                project = Project.objects.get(scpca_id=scpca_id)
                logger.info(f"Purging '{project}'")
                project.purge(delete_from_s3=update_s3_data)
            except Project.DoesNotExist:
                pass

        project, created = Project.objects.get_or_create(scpca_id=scpca_id)
        # Only import new projects. If old ones are desired they should be
        # purged and readded.
        if not created:
            continue

        project.abstract = project_data["abstract"]
        project.contact_email = project_data["contact_email"]
        project.contact_name = project_data["contact_name"]
        project.has_bulk_rna_seq = os.path.exists(project.input_bulk_metadata_path)
        project.has_spatial_data = utils.boolean_from_string(project_data.get("has_spatial", False))
        project.human_readable_pi_name = project_data["PI"]
        project.pi_name = project_data["submitter"]
        project.title = project_data["project_title"]
        project.save()

        if not project.scpca_id in os.listdir(common.INPUT_DATA_DIR):
            logger.warning(f"Metadata found for '{project}' but no s3 folder of that name exists.")
            continue

        logger.info(f"Importing '{project}' data")
        computed_files = project.load_data(scpca_sample_ids=scpca_sample_ids)
        samples_count = project.samples.count()
        if samples_count:
            logger.info(f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'")

        if update_s3_data:
            logger.info(f"Exporting '{project}' computed files to S3")
            for computed_file in computed_files:
                s3.upload_file(
                    computed_file.zip_file_path, settings.AWS_S3_BUCKET_NAME, computed_file.s3_key,
                )


class Command(BaseCommand):
    help = """Populates the database with data.

    The data should be contained in an S3 bucket called scpca-portal-inputs.

    The directory structure for this bucket should follow this pattern:
        /project_metadata.csv
        /SCPCP000001/libraries_metadata.csv
        /SCPCP000001/samples_metadata.csv
        /SCPCP000001/SCPCS000109/SCPCL000126_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000126_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000127_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000127_metadata.json

    The files will be zipped up and stats will be calculated for them.

    If run locally the zipped ComputedFiles will be copied to the
    "scpca-local-data" bucket.

    If run in the cloud the zipped ComputedFiles files will be copied
    to a stack-specific S3 bucket."""

    def add_arguments(self, parser):
        parser.add_argument("--reload-all", action="store_true")
        parser.add_argument("--reload-existing", action="store_true")
        parser.add_argument("--scpca-project-ids", nargs="+", type=str)
        parser.add_argument("--scpca-sample-ids", nargs="+", type=str)
        parser.add_argument("--update-s3", default=settings.UPDATE_S3_DATA, type=bool)

    def handle(self, *args, **options):
        load_data_from_s3(
            options["update_s3"],
            options["reload_existing"],
            options["reload_all"],
            options["scpca_project_ids"],
            options["scpca_sample_ids"],
        )

        cleanup_output_data_dir()
