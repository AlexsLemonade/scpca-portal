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
    state = models.TextField(choices=JobState.CHOICES, default=JobState.CREATED)
    submitted_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    terminated_at = models.DateTimeField(null=True)
    failure_reason = models.TextField(blank=True, null=True)
    critical_error = models.BooleanField(default=False)
    retry_on_termination = models.BooleanField(default=False)

    # Job Information Sent to AWS (via Request)
    batch_job_name = models.TextField(null=True)
    batch_job_queue = models.TextField(null=True)
    batch_job_definition = models.TextField(null=True)
    batch_container_overrides = models.JSONField(default=dict)

    # Job Information Defined from AWS (via Response)
    batch_job_id = models.TextField(null=True)
    batch_status = models.TextField(null=True)

    dataaset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL, related_name="jobs")

    def __str__(self):
        return f"Job {self.id} running in {self.batch_job_name}"

    def submit(self):
        """Submit a job via boto3, and update batch_job_id and state."""
        pass

    def terminate(self, has_error=False, can_retry=False):
        """
        Terminate the currently running job via boto3, and
        update state, critical_error (using has_error), and retry_on_termination (using can_retry).
        If both has_error and can_retry are true, the job will be retried after termination.
        """
        pass

    def get_retry_job(self):
        """
        Create and return a new Job instance to retry a terminated job via boto3,
        Updates attempt and state for the new job instance.
        """
        pass
