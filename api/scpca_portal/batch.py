from typing import Dict, List

import boto3
from botocore.client import Config

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
aws_batch = boto3.client("batch", config=Config(signature_version="s3v4"))


def submit_job(job) -> str | None:
    """
    Take a job instance to submit.
    Submit a job via boto3.
    Return the batch job ID on success, otherwise return None.
    """
    try:
        response = aws_batch.submit_job(
            jobName=job.batch_job_name,
            jobQueue=job.batch_job_queue,
            jobDefinition=job.batch_job_definition,
            containerOverrides=job.batch_container_overrides,
        )
    except Exception as error:
        logger.exception(
            f"Failed to terminate the job due to: \n\t{error}",
            job_id=job.pk,
            batch_job_id=job.batch_job_id,
        )
        return None

    logger.info(
        "Job submission complete.",
        job_id=job.pk,
        batch_job_id=job.batch_job_id,
    )
    return response["jobId"]


def terminate_job(job) -> bool:
    """
    Take a job instance to cancel or terminate.
    Terminate a job via boto3.
    Return True on success, otherwise return False.
    Jobs that are in STARTING or RUNNING are terminated, and set to FAILED.
    Jobs not yet in STARTING are cancelled.
    """
    try:
        aws_batch.terminate_job(jobId=job.batch_job_id, reason="Terminating job.")
    except Exception as error:
        logger.exception(
            f"Failed to terminate the job due to: \n\t{error}",
            job_id=job.pk,
            batch_job_id=job.batch_job_id,
        )
        return False

    logger.info(
        "Job termination complete.",
        job_id=job.pk,
        batch_job_id=job.batch_job_id,
    )
    return True


def get_job(batch_job_id: str) -> Dict | None:
    """
    Fetch an AWS Batch job for the given job ID.
    Return the fetched job on success, otherwise return None.
    """
    try:
        response = aws_batch.describe_jobs(jobs=[batch_job_id])
    except Exception as error:
        logger.exception(
            f"Failed to fetch AWS Batch job due to: \n\t{error}",
            batch_job_id=batch_job_id,
        )
        return None

    return response["jobs"][0]


def get_jobs(batch_job_ids: List[str]) -> List[Dict] | None:
    """
    Bulk fetch AWS Batch jobs by the given job IDs.
    Return a list of fetched jobs on success, otherwise return None.
    """
    max_limit = 100  # Limit of job IDs to send per request

    result = []

    try:
        for chunk in utils.get_chunk_list(batch_job_ids, max_limit):
            response = aws_batch.describe_jobs(jobs=chunk)
            result.extend(response["jobs"])
    except Exception as error:
        logger.exception(
            f"Failed to bulk fetch AWS Batch jobs due to: \n\t{error}",
        )
        return None

    return result
