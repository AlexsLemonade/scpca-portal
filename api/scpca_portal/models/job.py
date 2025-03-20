from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

import boto3

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import JobStates
from scpca_portal.models import Dataset
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class Job(TimestampedModel):
    class Meta:
        db_table = "jobs"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    # Internal Attributes
    attempt = models.PositiveIntegerField(default=1)  # Incremented on every retry
    critical_error = models.BooleanField(default=False)  # Set to True if the job is irrecoverable
    failure_reason = models.TextField(blank=True, null=True)
    retry_on_termination = models.BooleanField(default=False)
    state = models.TextField(choices=JobStates.choices, default=JobStates.CREATED)

    submitted_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    terminated_at = models.DateTimeField(null=True)

    # Job Information Sent to AWS (via Request)
    batch_job_name = models.TextField(null=True)
    batch_job_definition = models.TextField(null=True)
    batch_job_queue = models.TextField(null=True)
    batch_container_overrides = models.JSONField(default=dict)

    # Job Information Defined from AWS (via Response)
    batch_job_id = models.TextField(null=True)
    batch_status = models.TextField(null=True)  # Set by a cron job

    # Datasets should never be deleted
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL, related_name="jobs")

    def __str__(self):
        if self.batch_job_id:
            return f"Job {self.id} - {self.batch_job_id} - {self.state}"
        return f"Job {self.id} - {self.state}"

    @classmethod
    def get_project_job(cls, project_id: str, download_config_name: str, notify: bool = False):
        """
        Prepare a Job instance for a project without saving it to the db.
        """

        batch_job_name = f"{project_id}-{download_config_name}"
        notify_flag = "--notify" if notify else ""

        return cls(
            batch_job_name=batch_job_name,
            batch_job_queue=settings.AWS_BATCH_JOB_QUEUE_NAME,
            batch_job_definition=settings.AWS_BATCH_JOB_DEFINITION_NAME,
            batch_container_overrides={
                "command": [
                    "python",
                    "manage.py",
                    "generate_computed_file",
                    "--project-id",
                    project_id,
                    "--download-config-name",
                    download_config_name,
                    notify_flag,
                ],
            },
        )

    @classmethod
    def get_sample_job(
        cls,
        sample_id: str,
        download_config_name: str,
        notify: bool = False,
    ):
        """
        Prepare a Job instance for a sample without saving it to the db.
        """

        batch_job_name = f"{sample_id}-{download_config_name}"
        notify_flag = "--notify" if notify else ""

        return cls(
            batch_job_name=batch_job_name,
            batch_job_queue=settings.AWS_BATCH_JOB_QUEUE_NAME,
            batch_job_definition=settings.AWS_BATCH_JOB_DEFINITION_NAME,
            batch_container_overrides={
                "command": [
                    "python",
                    "manage.py",
                    "generate_computed_file",
                    "--sample-id",
                    sample_id,
                    "--download-config-name",
                    download_config_name,
                    notify_flag,
                ],
            },
        )

    @property
    def _batch(self):
        """
        boto3 client for AWS Batch.
        """
        return boto3.client("batch", region_name=settings.AWS_REGION)

    def submit(self) -> None:
        """
        Submit a job via boto3, update batch_job_id and state, and
        save the job object to the db.
        """
        try:
            response = self._batch.submit_job(
                jobName=self.batch_job_name,
                jobQueue=self.batch_job_queue,
                jobDefinition=self.batch_job_definition,
                containerOverrides=self.batch_container_overrides,
            )

            self.batch_job_id = response["jobId"]
            self.state = JobStates.SUBMITTED
            self.submitted_at = make_aware(datetime.now())

            self.save()

        except Exception as error:
            logger.exception(
                f"Failed to terminate the job due to: \n\t{error}",
                job_id=self.pk,
                batch_job_id=self.batch_job_id,
            )
            return False

        logger.info(
            "Job submission complete.",
            job_id=self.pk,
            batch_job_id=self.batch_job_id,
        )
        return True

    def terminate(self, retry_on_termination=False) -> bool:
        """
        Terminate the submitted and incomplete job via boto3, and update state.
        Return True if the job is successfully terminated or already terminated, otherwise False.
        Throw an error if failed to terminate the job.
        """

        if self.state in [JobStates.COMPLETED, JobStates.TERMINATED]:
            return self.state == JobStates.TERMINATED

        try:
            self._batch.terminate_job(jobId=self.batch_job_id, reason="Terminating job.")
            self.state = JobStates.TERMINATED
            self.retry_on_termination = retry_on_termination
            self.terminated_at = make_aware(datetime.now())

            self.save()

        except Exception as error:
            logger.exception(
                f"Failed to terminate the job due to: \n\t{error}",
                job_id=self.pk,
                batch_job_id=self.batch_job_id,
            )
            return False

        logger.info(
            "Job termination complete.",
            job_id=self.pk,
            batch_job_id=self.batch_job_id,
        )
        return True

    def get_retry_job(self):
        """
        Create and return a new Job instance to retry a terminated job via boto3,
        Updates attempt and state for the new job instance.
        Called only when critical_error is False and retry_on_termination is True.
        """
        pass
