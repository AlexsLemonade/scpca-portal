from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

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

    @staticmethod
    def get_mapped_job_state(batch_job_status: str) -> str:
        """
        Map the AWS Batch job status to the corresponding instance job state.
        Return the mapped instance state value,
        """
        state_mapping = {
            "SUBMITTED": JobStates.SUBMITTED,
            "PENDING": JobStates.SUBMITTED,
            "RUNNABLE": JobStates.SUBMITTED,
            "STARTING": JobStates.SUBMITTED,
            "RUNNING": JobStates.SUBMITTED,
            "SUCCEEDED": JobStates.COMPLETED,
            "FAILED": JobStates.COMPLETED,
        }

        return state_mapping[batch_job_status]

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
    def bulk_sync_state(cls) -> bool:
        """
        Sync all submitted job instances' states with AWS Batch job statuses.
        Call batch.get_jobs to fetch all the corresponding remote jobs.
        Update each job instance's state if it changes to COMPLETED, and update completed_at.
        If the remote status is 'FAILED', update failure_reason if it hasn't been set already.
        """
        submitted_jobs = cls.objects.filter(state=JobStates.SUBMITTED)
        batch_job_ids = [job.batch_job_id for job in submitted_jobs]

        if fetched_jobs := batch.get_jobs(batch_job_ids):
            # Map the fetched AWS jobs for easy lookup by batch_job_id
            aws_jobs = {
                job["jobId"]: {"status": job["status"], "statusReason": job.get("statusReason")}
                for job in fetched_jobs
            }

            jobs_to_update = []  # Store jobs to be updated in the db

            for job in submitted_jobs:
                aws_job = aws_jobs.get(job.batch_job_id)

                # TODO: How should we handle when no matched AWS job returned?
                # Currently, it continues without interruption, should we log, or raise an error?
                if not aws_job:
                    continue

                aws_job_status = aws_job["status"]
                mapped_job_state = job.get_mapped_job_state(aws_job_status)

                # Only update the job if the state has changed
                if job.state != mapped_job_state:
                    if aws_job_status == "FAILED" and not job.failure_reason:
                        job.failure_reason = aws_job["statusReason"]

                    job.state = mapped_job_state
                    job.completed_at = make_aware(datetime.now())
                    jobs_to_update.append(job)

            if jobs_to_update:
                cls.objects.bulk_update(jobs_to_update, ["state", "failure_reason", "completed_at"])

            return True

        return False

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

    def sync_state(self) -> bool:
        """
        Sync the submitted job state with the AWS Batch job status.
        Call batch.get_job to fetch the corresponding remote job.
        Update instance state if it changes to COMPLETED, and update completed_at.
        If the remote status is 'FAILED', update failure_reason if it hasn't been set already.
        """
        if self.state is not JobStates.SUBMITTED:
            return False

        if fetched_job := batch.get_job(self.batch_job_id):
            aws_job_status = fetched_job["status"]
            mapped_job_state = self.get_mapped_job_state(aws_job_status)

            # Only update the job if the state has changed
            if self.state != mapped_job_state:
                if aws_job_status == "FAILED" and not self.failure_reason:
                    self.failure_reason = fetched_job["statusReason"]

                self.state = mapped_job_state
                self.completed_at = make_aware(datetime.now())

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

    def get_retry_job(self):
        """
        Prepare a new Job instance to retry the terminated job.
        Set new instance's attempt to the base instance's attempt incremented by 1.
        """

        if self.state != JobStates.TERMINATED:
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
