from datetime import datetime
from typing import List

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import batch
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

    @classmethod
    def get_retry_jobs(cls) -> List[Self]:
        """
        Prepare new saved Job instances to retry terminated jobs as the base.
        Exclude those with retry_on_termination is False.
        Set batch fields from base jobs except batch_job_id, and increment attempt by 1.
        Bulk save the new instances and return them.
        """
        retry_jobs = []

        if jobs := Job.objects.filter(state=JobStates.TERMINATED.value, retry_on_termination=True):
            for job in jobs:
                retry_jobs.append(job.get_retry_job())

            Job.objects.bulk_create(retry_jobs)

        return retry_jobs

    def submit(self) -> bool:
        """
        Submit the job via batch.submit_job.
        Update batch_job_id and state, and
        save it to the db on success.
        """
        if self.state is not JobStates.CREATED:
            return False

        if job_id := batch.submit_job(self):
            self.batch_job_id = job_id
            self.state = JobStates.SUBMITTED
            self.submitted_at = make_aware(datetime.now())

            self.save()
            return True

        return False

    def terminate(self, retry_on_termination=False) -> bool:
        """
        Terminate the submitted, incomplete job via batch.terminate_job.
        Update state, retry_on_termination and terminated_at, and
        save it to the db on success.
        """
        if self.state in [JobStates.COMPLETED, JobStates.TERMINATED]:
            return self.state == JobStates.TERMINATED

        if batch.terminate_job(self):
            self.state = JobStates.TERMINATED
            self.retry_on_termination = retry_on_termination
            self.terminated_at = make_aware(datetime.now())

            self.save()
            return True

        return False

    def get_retry_job(self) -> Self | None:
        """
        Prepare a new unsaved Job instance to retry the terminated job.
        Exclude those with retry_on_termination is False.
        Set batch fields from the existing fields except batch_job_id, and increment attempt by 1.
        Return the new instance, otherwise None.
        """

        if self.state != JobStates.TERMINATED.value or not self.retry_on_termination:
            return None

        # TODO: How should we handle attempting critically failed jobs?
        # if self.critical_error:
        #     return None

        return Job(
            attempt=self.attempt + 1,
            batch_job_name=self.batch_job_name,
            batch_job_definition=self.batch_job_definition,
            batch_job_queue=self.batch_job_queue,
            batch_container_overrides=self.batch_container_overrides,
            dataset=self.dataset,
        )
