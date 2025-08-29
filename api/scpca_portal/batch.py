from typing import Dict, Iterable, List

from django.conf import settings
from django.template.defaultfilters import pluralize

import boto3
from botocore.client import Config

from scpca_portal import utils
from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
aws_batch = boto3.client(
    "batch", config=Config(signature_version="s3v4", region_name=settings.AWS_REGION)
)


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
            f"Failed to submit the job due to: \n\t{error}",
            job_id=job.pk,
            batch_job_id=job.batch_job_id,
        )
        return None

    logger.debug(
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

    logger.debug(
        "Job termination complete.",
        job_id=job.pk,
        batch_job_id=job.batch_job_id,
    )
    return True


def get_jobs(batch_jobs: Iterable["Job"]) -> List[Dict] | None:  # noqa: F821
    """
    Fetch AWS Batch job(s) for the given one or more job(s) in bulk.
    Raises Exception on failure.
    Return a list of fetched jobs on success.
    """
    max_limit = 100  # Limit of job IDs to send per request
    jobs = []

    if batch_job_ids := [job.batch_job_id for job in batch_jobs]:
        for chunk in utils.get_chunk_list(batch_job_ids, max_limit):
            try:
                response = aws_batch.describe_jobs(jobs=chunk)
                jobs.extend(response["jobs"])
            except Exception as error:
                logger.exception(
                    f"Failed to bulk fetch AWS Batch job{pluralize(len(chunk))} "
                    f"for job IDs: {', '.join(chunk)} due to: \n\t{error}"
                )
                raise

    logger.debug("AWS Job fetch complete.", batch_job_ids=batch_job_ids)

    return jobs
