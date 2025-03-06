from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

import boto3

from scpca_portal.enums import JobStates
from scpca_portal.models import Dataset
from scpca_portal.models.base import TimestampedModel


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
    def get_job(
        cls,
        batch_job_name: str = None,
        batch_job_queue: str = None,
        batch_job_definition: str = None,
        batch_container_overrides: dict = None,
    ):
        """
        Prepare a Job instance for AWS Batch without saving it to the db.
        """

        batch_job_name = batch_job_name or "DEFAULT_BATCH_JOB_NAME"
        batch_job_queue = batch_job_queue or "DEFAULT_BATCH_JOB_QUEUE"
        batch_job_definition = batch_job_definition or "DEFAULT_BATCH_JOB_DEFINITION"
        batch_container_overrides = batch_container_overrides or {"command": ["DEFAULT_COMMAND"]}

        return cls(
            batch_job_name=batch_job_name,
            batch_job_queue=batch_job_queue,
            batch_job_definition=batch_job_definition,
            batch_container_overrides=batch_container_overrides,
        )

    @property
    def _batch(self):
        """
        boto3 client for AWS Batch.
        """
        return boto3.client("batch", region_name=settings.AWS_REGION)

    def submit(self, resource_id: str = "", notify: bool = False) -> None:
        """Submit a job via boto3, update batch_job_id and state, and
        save the job object to the db"""

        notify_flag = "--notify" if notify else ""
        command = self.batch_container_overrides.get("command")
        command.extend([resource_id, notify_flag])

        response = self._batch.submit_job(
            jobName=self.batch_job_name,
            jobQueue=self.batch_job_queue,
            jobDefinition=self.batch_job_definition,
            containerOverrides={**self.batch_container_overrides, "command": command},
        )

        self.batch_job_id = response["jobId"]
        self.state = JobStates.SUBMITTED
        self.submitted_at = make_aware(datetime.now())

        self.save()

    def terminate(self, retry_on_termination=False):
        """
        Terminate the currently running job via boto3, and update state.
        Set critical_error to True if the job is irrecoverable.
        """
        pass

    def get_retry_job(self):
        """
        Create and return a new Job instance to retry a terminated job via boto3,
        Updates attempt and state for the new job instance.
        Called only when critical_error is False and retry_on_termination is True.
        """
        pass
