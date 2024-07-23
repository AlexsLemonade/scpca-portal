import subprocess
from pathlib import Path

from django.conf import settings

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


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


def download_data(bucket_name, scpca_project_id=None):
    command_list = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]
    if scpca_project_id:
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


def upload_s3_file(computed_file) -> None:
    """Upload a computed file to S3 using the AWS CLI tool."""

    aws_path = f"s3://{settings.AWS_S3_BUCKET_NAME}/{computed_file.s3_key}"
    command_parts = ["aws", "s3", "cp", str(computed_file.zip_file_path), aws_path]

    logger.info(f"Uploading {computed_file}")
    subprocess.check_call(command_parts)


def delete_s3_file(computed_file, force=False):
    # If we're not running in the cloud then we shouldn't try to
    # delete something from S3 unless force is set.
    if not settings.UPDATE_S3_DATA and not force:
        return False

    try:
        s3.delete_object(Bucket=computed_file.s3_bucket, Key=computed_file.s3_key)
    except Exception:
        logger.exception(
            "Failed to delete S3 object for Computed File.",
            computed_file=computed_file.id,
            s3_object=computed_file.s3_key,
        )
        return False

    return True


def create_download_url(self):
    """Creates a temporary URL from which the file can be downloaded."""
    if self.s3_bucket and self.s3_key:
        # Append the download date to the filename on download.
        date = utils.get_today_string()
        s3_key = Path(self.s3_key)

        return s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.s3_bucket,
                "Key": self.s3_key,
                "ResponseContentDisposition": (
                    f"attachment; filename = {s3_key.stem}_{date}{s3_key.suffix}"
                ),
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
        )
