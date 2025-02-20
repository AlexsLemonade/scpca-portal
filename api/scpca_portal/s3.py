import json
import subprocess
from collections import namedtuple
from pathlib import Path
from typing import Dict, List

from django.conf import settings

import boto3
from botocore.client import Config

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)
aws_s3 = boto3.client("s3", config=Config(signature_version="s3v4"))

S3_OBJECT_KEYS = [
    # format is as follows: (old_key, new_key, default_value)
    ("Key", "s3_key", ""),
    ("Size", "size_in_bytes", 0),
    ("ETag", "hash", ""),
]

# the strip removes the leading and trailing double quotes included in the hash value.
# the split removes the `-#` from end of the hash value, which represents
# the number of chunks the file was originally uploaded in.
S3_OBJECT_VALUES = {
    "hash": lambda hash_value: hash_value.strip('"').split("-")[0],
    "s3_key": lambda s3_key_value, prefix: s3_key_value.removeprefix(f"{prefix}/"),
}


def remove_listed_directories(listed_objects):
    """Returns cleaned list of object files without directories objects."""
    return [obj for obj in listed_objects if not obj["s3_key"].endswith("/")]


def list_bucket_objects(bucket: str) -> List[Dict]:
    """
    Queries the aws s3api for all of a bucket's objects
    and returns a list of dictionaries with properties of contained objects.
    """
    command_inputs = ["aws", "s3api", "list-objects", "--output", "json"]

    prefix = ""
    if "/" in bucket:
        bucket, prefix = bucket.split("/", 1)
        command_inputs.extend(["--prefix", prefix])
    command_inputs.extend(["--bucket", bucket])

    if "public" in bucket:
        command_inputs.append("--no-sign-request")

    try:
        result = subprocess.run(command_inputs, capture_output=True, text=True, check=True)
        raw_json_output = result.stdout
        json_output = json.loads(raw_json_output)
    except subprocess.CalledProcessError:
        logger.error("Either the request was malformed or there was a network error.")
        raise

    if "Contents" not in json_output:
        logger.info(f"Queried s3 bucket ({bucket}) is empty.")
        return []

    all_listed_objects = json_output.get("Contents")
    for listed_object in all_listed_objects:
        utils.transform_keys(listed_object, S3_OBJECT_KEYS)
        utils.transform_values(listed_object, S3_OBJECT_VALUES, prefix)

    return remove_listed_directories(all_listed_objects)


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


def download_files(original_files) -> bool:
    """Download all passed data file paths which have not previously been downloaded.'"""

    # NOTE: AWS Sync does one iteration per include flag.
    # This causes a tremendous slowdown when trying to sync a long list of specific files.
    # In order to overcome this we should sync once
    # per project folder's immediate child subdirectory or file.
    for bucket_path, download_paths in OriginalFile.get_bucket_paths(original_files).items():
        bucket_name, download_dir = bucket_path
        command_parts = [
            "aws",
            "s3",
            "sync",
            f"s3://{bucket_name / download_dir}",
            settings.INPUT_DATA_PATH / download_dir,
        ]
        command_parts.append("--exclude=*")
        command_parts.extend([f"--include={download_path}" for download_path in download_paths])

        if "public-test" in str(bucket_name):
            command_parts.append("--no-sign-request")

        try:
            subprocess.check_call(command_parts)
        except subprocess.CalledProcessError as error:
            logger.error(f"Files failed to download due to the following error:\n\t{error}")
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
