from django.db import models

from scpca_portal.enums import JobState
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
    state = models.TextField(choices=JobState.CHOICES, default=JobState.CREATED)

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
    batch_status = models.TextField(null=True)

    # Datasets should never be deleted
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL, related_name="jobs")

    def __str__(self):
        if self.batch_job_id:
            return f"Job {self.id} - {self.batch_job_id} - {self.state}"

        return f"Job {self.id} - {self.state}"

    def submit(self):
        """Submit a job via boto3, and update batch_job_id and state."""
        pass

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
