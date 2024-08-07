import subprocess
from collections import namedtuple
from pathlib import Path
from typing import List

from django.conf import settings

import boto3
from botocore.client import Config

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
aws_s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


def list_input_paths(
    relative_path: Path = Path(),
    *,
    bucket_path: Path = Path(common.INPUT_BUCKET_NAME),
    recursive: bool = True,
) -> List[Path]:
    """
    Queries a path on an inputted s3 bucket
    and returns bucket's existing content as a list of Path objects,
    relative to (without) the bucket prefix.
    """
    root_path = Path(*bucket_path.parts, *relative_path.parts)
    command_inputs = ["aws", "s3", "ls", f"s3://{root_path}"]

    if recursive:
        command_inputs.append("--recursive")

    if "public" in str(bucket_path):
        command_inputs.append("--no-sign-request")

    try:
        result = subprocess.run(command_inputs, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as error:
        logger.error(
            """
            `{}`: Cause of error not returned, note: folder must exist and be non-empty
            """.format(
                error
            )
        )
        return []

    # The `aws s3 ls <bucket>` command returns a list of two types of entries:
    # - Bucket Object Entries
    # - Bucket Prefix Entries
    # In order to create a standard API, where `entry.file_path` could be accessed
    # irrespective of the entry type, we've created two named tuples which follow the return format
    # of each of the bucket entry types.
    BucketObjectEntry = namedtuple(
        "BucketObjectEntry", ["date", "time", "size_in_bytes", "file_path"]
    )
    BucketPrefixEntry = namedtuple("BucketPrefixEntry", ["prefix_designation", "file_path"])
    bucket_entries = []

    for line in output.splitlines():
        if line.strip().startswith("PRE"):
            bucket_entries.append(BucketPrefixEntry._make(line.split()))
        else:
            bucket_entries.append(BucketObjectEntry._make(line.split()))

    file_paths = [Path(entry.file_path) for entry in bucket_entries]

    # recursive returns an absolute path (see docstring)
    if recursive:
        bucket_keys = Path(*bucket_path.parts[1:])
        return [entry.relative_to(bucket_keys) for entry in file_paths]

    return file_paths


def download_input_files(
    file_paths: List[Path], *, bucket_name: str = common.INPUT_BUCKET_NAME
) -> bool:
    """Download all passed data file paths which have not previously been downloaded.'"""
    command_parts = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]

    download_queue = [fp for fp in file_paths if not fp.exists()]
    # If download_queue is empty, exit early
    if not download_queue:
        return True

    command_parts.append("--exclude=*")
    command_parts.extend([f"--include={file_path}" for file_path in download_queue])

    if "public-test" in bucket_name:
        command_parts.append("--no-sign-request")

    try:
        subprocess.check_call(command_parts)
    except subprocess.CalledProcessError as error:
        logger.error(f"Data files failed to download due to the following error:\n\t{error}")
        return False

    return True


def download_input_metadata(*, bucket_name: str = common.INPUT_BUCKET_NAME) -> bool:
    """Download all metadata files to the local file system."""
    command_parts = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]

    command_parts.append("--exclude=*")
    command_parts.append("--include=*_metadata.*")

    if "public-test" in bucket_name:
        command_parts.append("--no-sign-request")

    try:
        subprocess.check_call(command_parts)
    except subprocess.CalledProcessError as error:
        logger.error(f"Metadata files failed to download due to the following error:\n\t{error}")
        return False

    return True


def delete_output_file(key: str) -> bool:
    # If we're not running in the cloud then we shouldn't try to
    # delete something from S3 unless force is set.
    if not settings.UPDATE_S3_DATA:
        return False

    try:
        aws_s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
    except Exception:
        logger.exception(
            "Failed to delete S3 object for Computed File.",
            s3_object=key,
        )
        return False

    return True


def upload_output_file(key: str) -> bool:
    """Upload a computed file to S3 using the AWS CLI tool."""

    local_path = common.OUTPUT_DATA_PATH / key
    aws_path = f"s3://{settings.AWS_S3_BUCKET_NAME}/{key}"
    command_parts = ["aws", "s3", "cp", local_path, aws_path]

    logger.info(f"Uploading Computed File {key}")
    try:
        subprocess.check_call(command_parts)
    except subprocess.CalledProcessError as error:
        logger.error(f"Computed file failed to upload due to the following error:\n\t{error}")
        return False

    return True


def generate_pre_signed_link(key: str, filename: str) -> str:
    return aws_s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET_NAME,
            "Key": key,
            "ResponseContentDisposition": (f"attachment; filename = {filename}"),
        },
        ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
    )
