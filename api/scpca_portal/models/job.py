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

FINAL_JOB_STATES = [JobStates.COMPLETED.value, JobStates.TERMINATED.value]


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
    state = models.TextField(choices=JobStates.choices, default=JobStates.CREATED.value)

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
    def update_job_state(job: Self, aws_job: dict) -> tuple[Self, bool]:
        """
        Map the AWS Batch job status to the corresponding instance job state.
        Update the instance state and timestamps if the state changes.
        Return the instance and a boolean indicating whether the instance was updated.
        """
        if aws_job.get("isCancelled") or aws_job.get("isTerminated"):
            job.state = JobStates.TERMINATED.value
            job.terminated_at = make_aware(datetime.now())

            return job, True

        state_mapping = {
            "SUCCEEDED": JobStates.COMPLETED.value,
            "FAILED": JobStates.COMPLETED.value,
        }

        aws_job_status = aws_job["status"]
        new_state = state_mapping.get(aws_job_status, JobStates.SUBMITTED.value)

        if job.state == new_state:
            return job, False

        if aws_job_status == "FAILED":
            job.failure_reason = aws_job["statusReason"]

        job.state = new_state
        job.completed_at = make_aware(datetime.now())

        return job, True

    @classmethod
    def get_dataset_job(cls, dataset: Dataset, notify: bool = False) -> Self:
        """
        Prepare a Job instance for a dataset without saving it to the db.
        """

        # TODO: we should allow for users to request no notification via Dataset.notify attr
        notify_flag = "--notify" if (not dataset.is_ccdl or notify) else ""

        return cls(
            batch_job_name=dataset.id,
            batch_job_queue=settings.AWS_BATCH_JOB_QUEUE_NAME,
            batch_job_definition=settings.AWS_BATCH_JOB_DEFINITION_NAME,
            batch_container_overrides={
                "command": [
                    "python",
                    "manage.py",
                    "generate_computed_file",
                    "--dataset-id",
                    str(dataset.id),
                    notify_flag,
                ],
            },
            dataset=dataset,
        )

    @classmethod
    def get_project_job(
        cls, project_id: str, download_config_name: str, notify: bool = False
    ) -> Self:
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
    ) -> Self:
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
    def create_terminated_retry_jobs(cls) -> List[Self]:
        """
        Queries terminated jobs that are flagged for retry.
        Removes retry flag so matched jobs will not be queried again.
        Creates new jobs for submitting.
        Returns newly created jobs.
        """
        retry_jobs = []

        if jobs := Job.objects.filter(state=JobStates.TERMINATED.value, retry_on_termination=True):
            for job in jobs:
                retry_jobs.append(job.get_retry_job())

            if Job.objects.bulk_create(retry_jobs):
                jobs.update(retry_on_termination=False)

        return retry_jobs

    @classmethod
    def submit_created(cls) -> List[Self]:
        """
        Submits all saved CREATED jobs to AWS Batch.
        Updates each job instance's batch_job_id, state, and submitted_at, and
        saves the changes to the db on success.
        Returns all the submitted jobs.
        """
        submitted_jobs = []

        if jobs := Job.objects.filter(state=JobStates.CREATED.value):
            for job in jobs:
                if aws_job_id := batch.submit_job(job):
                    job.batch_job_id = aws_job_id
                    job.state = JobStates.SUBMITTED.value
                    job.submitted_at = make_aware(datetime.now())
                    submitted_jobs.append(job)

            Job.objects.bulk_update(submitted_jobs, ["batch_job_id", "state", "submitted_at"])

        return submitted_jobs

    @classmethod
    def terminate_submitted(cls) -> List[Self]:
        """
        Terminates all submitted, incomplete jobs on AWS Batch.
        Updates each instance's state and terminated_at, and
        saves the changes to the db on success.
        Returns all the terminated jobs.
        """
        terminated_jobs = []

        if jobs := Job.objects.filter(state=JobStates.SUBMITTED.value):
            for job in jobs:
                if batch.terminate_job(job):
                    job.state = JobStates.TERMINATED.value
                    job.terminated_at = make_aware(datetime.now())
                    terminated_jobs.append(job)

            Job.objects.bulk_update(terminated_jobs, ["state", "terminated_at"])

        return terminated_jobs

    # NOTE: This will be refactored later (e.g., save itself before job submission for job.id)
    @classmethod
    def bulk_sync_state(cls) -> bool:
        """
        Sync all submitted job instances' states with the remote AWS Batch job statuses.
        Update each job instance's state if it changes to COMPLETED, and update completed_at.
        If the remote status is 'FAILED', update failure_reason if it hasn't been set already.
        """
        if submitted_jobs := cls.objects.filter(state=JobStates.SUBMITTED.value):
            if fetched_jobs := batch.get_jobs(submitted_jobs):
                # Map the fetched AWS jobs for easy lookup by batch_job_id
                aws_jobs = {job["jobId"]: job for job in fetched_jobs}

                synced_jobs = []

                for job in submitted_jobs:
                    if aws_job := aws_jobs.get(job.batch_job_id):
                        updated_job, updated = cls.update_job_state(job, aws_job)
                        if updated:
                            synced_jobs.append(updated_job)
                        else:
                            continue

                if synced_jobs:
                    cls.objects.bulk_update(
                        synced_jobs,
                        ["state", "failure_reason", "completed_at", "terminated_at"],
                    )

                return True

        return False

    def submit(self) -> bool:
        """
        Submits the CREATED job to AWS Batch.
        Updates batch_job_id, state, and submitted_at, and
        saves the changes to the db on success.
        """
        if self.state is not JobStates.CREATED.value:
            return False

        if job_id := batch.submit_job(self):
            self.batch_job_id = job_id
            self.state = JobStates.SUBMITTED.value
            self.submitted_at = make_aware(datetime.now())

            self.save()
            return True

        return False

    def sync_state(self) -> bool:
        """
        Syncs the submitted job state with the remote AWS Batch job status.
        Updates instance state if it changes to COMPLETED, and update completed_at.
        If the remote status is 'FAILED', update failure_reason if it hasn't been set already.
        """
        if self.state is not JobStates.SUBMITTED.value:
            return False

        if fetched_jobs := batch.get_jobs([self]):
            aws_job = fetched_jobs[0]
            updated_job, updated = self.update_job_state(self, aws_job)

            if updated:
                updated_job.save()
                return True

        return False

    def terminate(self, retry_on_termination: bool = False) -> bool:
        """
        Terminates the submitted, incomplete job on AWS Batch.
        Updates state, retry_on_termination, and terminated_at, and
        saves the changes to the db on success.
        """
        if self.state in FINAL_JOB_STATES:
            return self.state == JobStates.TERMINATED.value

        if batch.terminate_job(self):
            self.state = JobStates.TERMINATED.value
            self.retry_on_termination = retry_on_termination
            self.terminated_at = make_aware(datetime.now())

            self.save()
            return True

        return False

    def get_retry_job(self) -> Self | bool:
        """
        Prepares a new Job instance to retry the terminated job.
        Returns newly instantiated jobs.
        """
        if self.state not in FINAL_JOB_STATES:
            return False

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
