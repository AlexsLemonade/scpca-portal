import csv
import logging
import shutil
import subprocess
from argparse import BooleanOptionalAction
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

import boto3
from botocore.client import Config

from scpca_portal import common
from scpca_portal.models import Contact, Project

ALLOWED_SUBMITTERS = {
    "christensen",
    "dyer_chen",
    "gawad",
    "green_mulcahy_levy",
    "mullighan",
    "murphy_chen",
    "pugh",
    "teachey_tan",
    "wu",
    "rokita",
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

    @staticmethod
    def clean_up_output_data():
        for path in Path(common.OUTPUT_DATA_PATH).glob("*"):
            path.unlink(missing_ok=True)

    @staticmethod
    def configure_aws_cli(**params):
        commands = [
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#payload-signing-enabled
            "aws configure set default.s3.payload_signing_enabled false",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-concurrent-requests
            "aws configure set default.s3.max_concurrent_requests "
            f"{params['s3_max_concurrent_requests']}",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#multipart-chunksize
            "aws configure set default.s3.multipart_chunksize "
            f"{params['s3_multipart_chunk_size']}MB",
        ]
        if params["s3_max_bandwidth"] is not None:
            commands.append(
                # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-bandwidth
                f"aws configure set default.s3.max_bandwidth {params['s3_max_bandwidth']}MB/s",
            )

        for command in commands:
            subprocess.check_call(command.split())

    @staticmethod
    def download_data(bucket_name, scpca_project_id=None, scpca_sample_id=None):
        command_list = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]
        if scpca_sample_id:
            command_list.extend(
                (
                    "--exclude=*",  # Must precede include patterns.
                    "--include=project_metadata.csv",
                    f"--include=merged/{scpca_project_id}*",
                    f"--include={scpca_project_id}/{scpca_sample_id}*",
                )
            )
        elif scpca_project_id:
            command_list.extend(
                (
                    "--exclude=*",  # Must precede include patterns.
                    "--include=project_metadata.csv",
                    f"--include=merged/{scpca_project_id}*",
                    f"--include={scpca_project_id}*",
                )
            )
        else:
            command_list.append("--delete")

        if "public-test" in bucket_name:
            command_list.append("--no-sign-request")

        subprocess.check_call(command_list)

    def add_arguments(self, parser):
        parser.add_argument("--input-bucket-name", type=str, default="scpca-portal-inputs")
        parser.add_argument(
            "--clean-up-input-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )
        parser.add_argument(
            "--clean-up-output-data", action=BooleanOptionalAction, default=settings.PRODUCTION
        )
        parser.add_argument("--max-workers", type=int, default=10)
        parser.add_argument("--reload-all", action="store_true", default=False)
        parser.add_argument("--reload-existing", action="store_true", default=False)
        parser.add_argument("--s3-max-bandwidth", type=int, default=None, help="In MB/s")
        parser.add_argument("--s3-max-concurrent-requests", type=int, default=10)
        parser.add_argument("--s3-multipart-chunk-size", type=int, default=8, help="In MB")
        parser.add_argument("--scpca-project-id", type=str)
        parser.add_argument("--scpca-sample-id", type=str)
        parser.add_argument("--skip-sync", action="store_true", default=False)
        parser.add_argument(
            "--update-s3", action=BooleanOptionalAction, default=settings.UPDATE_S3_DATA
        )

    def clean_up_input_data(self):
        shutil.rmtree(common.INPUT_DATA_PATH / self.project.scpca_id, ignore_errors=True)

    def handle(self, *args, **kwargs):
        self.configure_aws_cli(**kwargs)
        self.load_data(**kwargs)

    def load_data(
        self,
        allowed_submitters: set[str] = None,
        input_bucket_name: str = "scpca-portal-inputs",
        **kwargs,
    ):
        """Loads data from S3. Creates projects and loads data for them."""

        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prepare data output directory.
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)
        common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        allowed_submitters = allowed_submitters or ALLOWED_SUBMITTERS
        project_id = kwargs.get("scpca_project_id")
        sample_id = kwargs.get("scpca_sample_id")

        if not kwargs.get("skip_sync"):
            self.download_data(
                input_bucket_name, scpca_project_id=project_id, scpca_sample_id=sample_id
            )

        project_samples_mapping = {
            project_path.name: set((sd.name for sd in project_path.iterdir() if sd.is_dir()))
            for project_path in common.INPUT_DATA_PATH.iterdir()
            if project_path.is_dir()
        }

        with open(Project.get_input_project_metadata_file_path()) as project_csv:
            project_list = list(csv.DictReader(project_csv))

        for project_data in project_list:
            scpca_project_id = project_data["scpca_project_id"]
            if project_id and project_id != scpca_project_id:
                continue

            if scpca_project_id not in project_samples_mapping:
                logger.warning(
                    f"Metadata found for '{scpca_project_id}' but no s3 folder of that name exists."
                )
                return

            if project_data["submitter"] not in allowed_submitters:
                logger.warning("Project submitter  is not the white list.")
                continue

            if project := Project.objects.filter(scpca_id=scpca_project_id).first():
                # Purge existing projects so they can be re-added.
                if kwargs["reload_all"] or kwargs["reload_existing"]:
                    logger.info(f"Purging '{project}")
                    project.purge(delete_from_s3=kwargs["update_s3"])
                # Only import new projects.
                # If old ones are desired they should be purged and re-added.
                else:
                    logger.info(f"'{project}' already exists. Use --reload-existing to re-import.")
                    continue

            project = Project.get_from_dict(project_data)
            logger.info(f"Importing '{project}' data")
            project.save()
            Contact.bulk_create_from_project_data(project_data, project)

            project.load_data(sample_id=sample_id, **kwargs)
            if samples_count := project.samples.count():
                logger.info(
                    f"Created {samples_count} sample{pluralize(samples_count)} for '{project}'"
                )

            if kwargs["clean_up_input_data"]:
                logger.info(f"Cleaning up '{project}' input data")
                self.clean_up_input_data()

            if kwargs["clean_up_output_data"]:
                logger.info("Cleaning up output directory")
                self.clean_up_output_data()
