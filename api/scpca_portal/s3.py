import json
import subprocess
from pathlib import Path
from typing import Dict, List

from django.conf import settings

import boto3
from botocore.client import Config

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.original_file import OriginalFile

logger = get_and_configure_logger(__name__)
aws_s3 = boto3.client(
    "s3", config=Config(signature_version="s3v4", region_name=settings.AWS_REGION)
)

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


def _exclude_objects_with_key_substrings(
    bucket_objects: List[Dict], substrings: List[str]
) -> List[Dict]:
    """
    Return filtered version of passed bucket objects,
    removing all objects whose s3 keys include any of the passed substrings.
    """
    if not substrings:
        return bucket_objects

    return [
        bucket_object
        for bucket_object in bucket_objects
        if not any(sub in bucket_object["s3_key"] for sub in substrings)
    ]


def _remove_listed_directories(listed_objects):
    """Returns cleaned list of object files without directories objects."""
    return [obj for obj in listed_objects if not obj["s3_key"].endswith("/")]


def list_bucket_objects(bucket: str, *, excluded_key_substrings: List[str] = []) -> List[Dict]:
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

    bucket_objects = json_output.get("Contents")
    for bucket_object in bucket_objects:
        utils.transform_keys(bucket_object, S3_OBJECT_KEYS)
        utils.transform_values(bucket_object, S3_OBJECT_VALUES, prefix)
    filtered_objects = _exclude_objects_with_key_substrings(bucket_objects, excluded_key_substrings)

    return _remove_listed_directories(filtered_objects)


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


def upload_file(key: str, bucket_name: str, local_path: Path) -> bool:
    """Upload a file to S3 using the AWS CLI tool."""

    aws_path = f"s3://{bucket_name}/{key}"
    command_parts = ["aws", "s3", "cp", local_path, aws_path]

    logger.info(f"Uploading File {key}")
    try:
        subprocess.check_call(command_parts)
    except subprocess.CalledProcessError as error:
        logger.error(f"File failed to upload due to the following error:\n\t{error}")
        return False

    return True


def check_file_empty(key: str, bucket: str) -> bool:
    """
    Checks to see if the passed bucket and key correspond to an empty file.
    """
    command_parts = ["aws", "s3api", "head-object", "--bucket", bucket, "--key", key]

    try:
        result = subprocess.run(command_parts, capture_output=True, text=True, check=True)
        raw_json_output = result.stdout
        json_output = json.loads(raw_json_output)
    except subprocess.CalledProcessError:
        logger.error("Either the request was malformed or there was a network error.")
        raise

    return json_output["ContentLength"] == 0


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
