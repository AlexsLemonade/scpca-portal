import csv
import logging
import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.models import ComputedFile, Project

ALLOWED_SUBMITTERS = {
    "christensen",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "mullighan",
    "murphy_chen",
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
        parser.add_argument("--scpca-project-id", action="extend", nargs="+", type=str)
        parser.add_argument("--scpca-sample-id", action="extend", nargs="+", type=str)
        parser.add_argument("--skip-sync", action="store_true", default=False)
        parser.add_argument("--update-s3", action="store_true", default=settings.UPDATE_S3_DATA)

    def handle(self, *args, **options):
        load_data_from_s3(
            reload_all=options["reload_all"],
            reload_existing=options["reload_existing"],
            scpca_project_ids=options["scpca_project_id"] or (),
            scpca_sample_ids=options["scpca_sample_id"] or (),
            skip_input_bucket_sync=options["skip_sync"],
            update_s3_data=options["update_s3"],
        )
        cleanup_output_data_dir()


def cleanup_output_data_dir():
    cleanup_items = (ComputedFile.README_FILE_NAME, ComputedFile.README_SPATIAL_FILE_NAME, "*.tsv")
    for item in cleanup_items:
        for path in Path(common.OUTPUT_DATA_DIR).glob(item):
            path.unlink()


def load_data_from_s3(
    allowed_submitters: set = ALLOWED_SUBMITTERS,
    input_bucket_name: str = "scpca-portal-inputs",
    reload_all: bool = False,
    reload_existing: bool = False,
    scpca_project_ids=(),
    scpca_sample_ids=(),
    skip_input_bucket_sync: bool = False,
    update_s3_data: bool = False,
):
    """Loads data from S3. Creates projects and loads data for them."""

    # Prepare data input directory.
    os.makedirs(common.INPUT_DATA_DIR, exist_ok=True)

    # Prepare data output directory.
    shutil.rmtree(common.OUTPUT_DATA_DIR, ignore_errors=True)
    os.mkdir(common.OUTPUT_DATA_DIR)

    if not skip_input_bucket_sync:
        command_list = [
            "aws",
            "s3",
            "sync",
            f"s3://{input_bucket_name}",
            common.INPUT_DATA_DIR,
        ]
        if "public-test" in input_bucket_name:
            command_list.append("--no-sign-request")

        scpca_ids = list(scpca_project_ids) + list(scpca_sample_ids)
        if scpca_ids:
            command_list.extend(
                (
                    "--exclude=*",  # Must precede include patterns.
                    "--include=project_metadata.csv",
                )
            )

            if scpca_sample_ids:
                command_list.extend(
                    (
                        "--include=*/samples_metadata.csv",
                        "--include=*_bulk_metadata.tsv",
                        "--include=*_bulk_quant.tsv",
                    )
                )
            command_list.extend((f"--include=*{scpca_id}*" for scpca_id in scpca_ids))
        else:
            command_list.append("--delete")

        subprocess.check_call(command_list)

    if reload_all:
        logger.info("Purging all projects")
        for project in Project.objects.order_by("scpca_id"):
            project.purge(delete_from_s3=update_s3_data)

    with open(Project.get_input_project_metadata_file_path()) as project_csv:
        project_list = list(csv.DictReader(project_csv))
    for project_data in project_list:
        scpca_id = project_data["scpca_project_id"]
        if scpca_project_ids and not scpca_sample_ids and scpca_id not in scpca_project_ids:
            continue

        if project_data["submitter"] not in allowed_submitters:
            continue

        # Purge existing projects so they can be re-added.
        if reload_existing:
            try:
                project = Project.objects.get(scpca_id=scpca_id)
                logger.info(f"Purging '{project}'")
                project.purge(delete_from_s3=update_s3_data)
            except Project.DoesNotExist:
                pass

        project, created = Project.objects.get_or_create(scpca_id=scpca_id)
        # Only import new projects. If old ones are desired they should be
        # purged and re-added.
        if not created:
            logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
            continue

        project.abstract = project_data["abstract"]
        project.contact_email = project_data["contact_email"]
        project.contact_name = project_data["contact_name"]
        project.has_bulk_rna_seq = utils.boolean_from_string(project_data.get("has_bulk", False))
        project.has_cite_seq_data = utils.boolean_from_string(project_data.get("has_CITE", False))
        project.has_multiplexed_data = utils.boolean_from_string(
            project_data.get("has_multiplex", False)
        )
        project.has_spatial_data = utils.boolean_from_string(project_data.get("has_spatial", False))
        project.human_readable_pi_name = project_data["PI"]
        project.pi_name = project_data["submitter"]
        project.title = project_data["project_title"]
        project.save()

        if project.scpca_id not in os.listdir(common.INPUT_DATA_DIR):
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
                    computed_file.zip_file_path,
                    settings.AWS_S3_BUCKET_NAME,
                    computed_file.s3_key,
                )
