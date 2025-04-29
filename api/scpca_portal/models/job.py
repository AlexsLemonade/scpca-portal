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

FINAL_JOB_STATES = [JobStates.SUCCEEDED, JobStates.FAILED, JobStates.TERMINATED]


class Job(TimestampedModel):
    class Meta:
        db_table = "jobs"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    # Internal Attributes
    attempt = models.PositiveIntegerField(default=1)  # Incremented on every retry
    failure_reason = models.TextField(blank=True, null=True)
    state = models.TextField(choices=JobStates.choices, default=JobStates.CREATED)

    submitted_at = models.DateTimeField(null=True)
    succeeded_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)  # TODO: Removed in #1210
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
    def get_job_state(aws_job: dict) -> tuple[str, str | None]:
        """
        Maps AWS Batch status to a corresponding local Job state.
        Returns the local state and AWS Batch status reason for failed or terminated jobs.
        """
        status = aws_job.get("status")
        reason = aws_job.get("statusReason")

        match status:
            case "SUCCEEDED":
                return JobStates.SUCCEEDED, None

            case "FAILED":
                if aws_job.get("isCancelled") or aws_job.get("isTerminated"):
                    return JobStates.TERMINATED, reason
                return JobStates.FAILED, reason

            case _:
                return JobStates.SUBMITTED, None

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
    def create_retry_jobs(cls, jobs: List[Self]) -> List[Self]:
        """
        Creates new jobs to retry the given jobs.
        Returns the newly created retry jobs.
        """
        retry_jobs = []

        for job in jobs:
            retry_jobs.append(job.get_retry_job())

        cls.bulk_update_state(jobs)
        cls.objects.bulk_create(retry_jobs)

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
        Updates each instance's state and completed_at, and
        saves the changes to the db on success.
        Returns all the terminated jobs.
        """
        failure_reason = "Terminated SUBMITTED"
        terminated_jobs = []

        if jobs := cls.objects.filter(state=JobStates.SUBMITTED):
            for job in jobs:
                if batch.terminate_job(job):
                    job.state = JobStates.TERMINATED
                    job.failure_reason = failure_reason
                    job.apply_state_at()
                    terminated_jobs.append(job)

            cls.bulk_update_state(terminated_jobs)

        return terminated_jobs

    @classmethod
    def bulk_update_state(cls, synced_jobs: List[Self]) -> None:
        """
        Bulk updates states of the given jobs and their associated datasets.
        """
        cls.objects.bulk_update(
            synced_jobs,
            [
                "state",
                "submitted_at",
                "succeeded_at",
                "failed_at",
                "failure_reason",
                "terminated_at",
            ],
        )

        Dataset.update_from_last_jobs([job.dataset for job in synced_jobs])

    @classmethod
    def bulk_sync_state(cls) -> bool:
        """
        Syncs all submitted jobs' states with the remote AWS Batch job statuses.
        Saves each job and its associated dataset if the state changes.
        """
        submitted_jobs = cls.objects.filter(state=JobStates.SUBMITTED)

        if not submitted_jobs.exists():
            return False

        fetched_jobs = batch.get_jobs(submitted_jobs)

        if not fetched_jobs:
            return False

        # Map the fetched AWS jobs for easy lookup by batch_job_id
        aws_jobs = {job["jobId"]: job for job in fetched_jobs}

        synced_jobs = []

        for job in submitted_jobs:
            if aws_job := aws_jobs.get(job.batch_job_id):
                new_state, failure_reason = cls.get_job_state(aws_job)

                if new_state != job.state:
                    job.state = new_state
                    job.failure_reason = failure_reason
                    job.update_state_at()
                    synced_jobs.append(job)
                else:
                    continue

        if synced_jobs:
            cls.bulk_update_state(synced_jobs)
            return True

        return False

    def update_state_at(self, save=False) -> None:
        """
        Sets timestamp fields, *_at, based on the latest job state.
        """
        timestamp = make_aware(datetime.now())

        match self.state:
            case JobStates.SUBMITTED:
                self.submitted_at = timestamp
            case JobStates.SUCCEEDED:
                self.succeeded_at = timestamp
            case JobStates.FAILED:
                self.failed_at = timestamp
            case JobStates.TERMINATED:
                self.terminated_at = timestamp

        if save:
            self.save()

    def submit(self) -> bool:
        """
        Submits the CREATED job to AWS Batch.
        Updates batch_job_id, state, and submitted_at, and
        saves the changes to the db on success.
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
        Sync the submitted job state with the remote AWS Batch job status.
        Save the job and its associated dataset if the state changes.
        """
        if self.state is not JobStates.SUBMITTED:
            return False

        if aws_jobs := batch.get_jobs([self]):
            new_state, failure_reason = self.get_job_state(aws_jobs[0])

            if new_state != self.state:
                self.state = new_state
                self.failure_reason = failure_reason
                self.update_state_at()

                Job.bulk_update_state([self])

                return True

        return False

    def terminate(self) -> bool:
        """
        Terminates the submitted, incomplete job on AWS Batch.
        Updates state and terminated_at, and
        saves the changes to the db on success.
        """
        if self.state in FINAL_JOB_STATES:
            return self.state == JobStates.TERMINATED

        failure_reason = "Terminated SUBMITTED"

        if batch.terminate_job(self):
            self.state = JobStates.TERMINATED
            self.failure_reason = failure_reason
            self.apply_state_at()

            Job.bulk_update_state([self])

            return True

        return False

    def get_retry_job(self) -> Self | bool:
        """
        Prepares a new Job instance for retry.
        Returns newly instantiated jobs.
        """
        if self.state not in FINAL_JOB_STATES:
            return False

        Job.bulk_update_state([self])

        return Job(
            attempt=self.attempt + 1,
            batch_job_name=self.batch_job_name,
            batch_job_definition=self.batch_job_definition,
            batch_job_queue=self.batch_job_queue,
            batch_container_overrides=self.batch_container_overrides,
            dataset=self.dataset,
        )
