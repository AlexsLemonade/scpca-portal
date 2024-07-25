import subprocess
from collections import namedtuple
from pathlib import Path
from typing import List

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


def list_input_paths(
    relative_path: Path = Path(),
    *,
    bucket_path: Path = Path(common.INPUT_BUCKET_NAME),
    recursive: bool = True,
):
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


def download_input_files(file_paths: List[Path], *, bucket_name: str = common.INPUT_BUCKET_NAME):
    """Download all passed data file paths which have not previously been downloaded.'"""
    command_parts = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]

    download_queue = [fp for fp in file_paths if not fp.exists()]
    # If download_queue is empty, exit early
    if not download_queue:
        return

    command_parts.append("--exclude=*")
    command_parts.extend([f"--include={file_path}" for file_path in download_queue])

    if "public-test" in bucket_name:
        command_parts.append("--no-sign-request")

    subprocess.check_call(command_parts)


def download_input_metadata(*, bucket_name: str = common.INPUT_BUCKET_NAME):
    """Download all metadata files to the local file system."""
    command_parts = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]

    command_parts.append("--exclude=*")
    command_parts.append("--include=*_metadata.*")

    if "public-test" in bucket_name:
        command_parts.append("--no-sign-request")

    subprocess.check_call(command_parts)


def delete_s3_file(computed_file, force: bool = False):
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
