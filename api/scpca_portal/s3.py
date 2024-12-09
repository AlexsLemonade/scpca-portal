import subprocess
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import List

from django.conf import settings

import boto3
from botocore.client import Config

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
aws_s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


def list_input_paths(
    relative_path: Path,
    bucket_name: str,
    *,
    recursive: bool = True,
) -> List[Path]:
    """
    Queries a path on an inputted s3 bucket
    and returns bucket's existing content as a list of Path objects,
    relative to (without) the bucket prefix.
    """
    bucket_path = Path(bucket_name)
    root_path = Path(*bucket_path.parts, *relative_path.parts)
    command_inputs = ["aws", "s3", "ls", f"s3://{root_path}"]

    if recursive:
        command_inputs.append("--recursive")
    # Note: when recursive=False, if there is no traling slash at the end of the s3 resource path,
    # dir contents will not be listed, but rather the entry located at the relative path itself
    else:
        command_inputs[-1] += "/"

    if "public" in str(bucket_path):
        command_inputs.append("--no-sign-request")

    try:
        result = subprocess.run(command_inputs, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as error:
        logger.warning(
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


def download_input_files(file_paths: List[Path], bucket_name: str) -> bool:
    """Download all passed data file paths which have not previously been downloaded.'"""

    # NOTE: AWS Sync does one iteration per include flag.
    # This causes a tremendous slowdown when trying to sync a long list of specific files.
    # In order to overcome this we should sync once
    # per project folder's immediate child subdirectory or file.
    download_queue = defaultdict(list)

    for file_path in file_paths:
        if not file_path.exists():

            # default to project folder for immediately nested files
            bucket_path = Path(file_path.parts[0])

            if len(file_path.parts) > 2:
                # append the subdirectory to the parent directory to form the bucket_path
                bucket_path /= file_path.parts[1]

            download_queue[bucket_path].append(file_path.relative_to(bucket_path))

    for bucket_path, project_file_paths in download_queue.items():
        command_parts = [
            "aws",
            "s3",
            "sync",
            f"s3://{bucket_name}/{bucket_path}",
            settings.INPUT_DATA_PATH / bucket_path,
        ]
        command_parts.append("--exclude=*")
        command_parts.extend([f"--include={file_path}" for file_path in project_file_paths])

        if "public-test" in bucket_name:
            command_parts.append("--no-sign-request")

        try:
            subprocess.check_call(command_parts)
        except subprocess.CalledProcessError as error:
            logger.error(f"Data files failed to download due to the following error:\n\t{error}")
            return False

    return True


def download_input_metadata(bucket_name: str) -> bool:
    """Download all metadata files to the local file system."""
    command_parts = ["aws", "s3", "sync", f"s3://{bucket_name}", settings.INPUT_DATA_PATH]

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


def delete_output_file(key: str, bucket_name: str) -> bool:
    """Delete file a remote file hosted on s3."""
    try:
        aws_s3.delete_object(Bucket=bucket_name, Key=key)
    except Exception:
        logger.exception(
            "Failed to delete S3 object for Computed File.",
            s3_object=key,
        )
        return False

    return True


def upload_output_file(key: str, bucket_name: str) -> bool:
    """Upload a computed file to S3 using the AWS CLI tool."""

    local_path = settings.OUTPUT_DATA_PATH / key
    aws_path = f"s3://{bucket_name}/{key}"
    command_parts = ["aws", "s3", "cp", local_path, aws_path]

    logger.info(f"Uploading Computed File {key}")
    try:
        subprocess.check_call(command_parts)
    except subprocess.CalledProcessError as error:
        logger.error(f"Computed file failed to upload due to the following error:\n\t{error}")
        return False

    return True


def generate_pre_signed_link(filename: str, key: str, bucket_name: str) -> str:
    return aws_s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": bucket_name,
            "Key": key,
            "ResponseContentDisposition": (f"attachment; filename = {filename}"),
        },
        ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
    )
