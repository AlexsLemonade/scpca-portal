from datetime import datetime
from typing import List

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import batch, common
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
    state = models.TextField(choices=JobStates.choices, default=JobStates.PENDING)

    pending_at = models.DateTimeField(auto_now_add=True)
    processing_at = models.DateTimeField(null=True)
    succeeded_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
    failed_reason = models.TextField(blank=True, null=True)
    terminated_at = models.DateTimeField(null=True)
    terminated_reason = models.TextField(blank=True, null=True)

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

    # Maximum size of a dataset in GB in order to be accommodated by the fargate pipeline
    # Number should be half of max fargate ephemeral storage (which is 200 GB)
    # Each instance downloads all dataset files, copies them to a zip file, and uploads the zip file
    MAX_FARGATE_SIZE_IN_BYTES = 100 * common.GB_IN_BYTES

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
                return JobStates.PROCESSING, None

    @classmethod
    def get_dataset_job(cls, dataset: Dataset, notify: bool = False) -> Self:
        """
        Prepare a Job instance for a dataset without saving it to the db.
        """

        # dynamically choose queue based on dataset size
        batch_job_queue = settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME
        batch_job_definition = settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
        if dataset.estimated_size_in_bytes > Job.MAX_FARGATE_SIZE_IN_BYTES:
            batch_job_queue = settings.AWS_BATCH_EC2_JOB_QUEUE_NAME
            batch_job_definition = settings.AWS_BATCH_EC2_JOB_DEFINITION_NAME

        batch_container_overrides = {
            "command": [
                "python",
                "manage.py",
                "process_dataset",
                "--dataset-id",
                str(dataset.id),
            ],
        }
        # TODO: we should allow for users to request no notification via Dataset.notify attr
        if not dataset.is_ccdl or notify:
            batch_container_overrides["command"].append("--notify")

        return cls(
            batch_job_name=str(dataset.id),
            batch_job_queue=batch_job_queue,
            batch_job_definition=batch_job_definition,
            batch_container_overrides=batch_container_overrides,
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

        command = [
            "python",
            "manage.py",
            "generate_computed_file",
            "--project-id",
            project_id,
            "--download-config-name",
            download_config_name,
        ]

        if notify:
            command.extend(["--notify"])

        return cls(
            batch_job_name=batch_job_name,
            batch_job_queue=settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME,
            batch_job_definition=settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME,
            batch_container_overrides={"command": command},
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

        command = [
            "python",
            "manage.py",
            "generate_computed_file",
            "--sample-id",
            sample_id,
            "--download-config-name",
            download_config_name,
        ]

        if notify:
            command.extend("--notify")

        return cls(
            batch_job_name=batch_job_name,
            batch_job_queue=settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME,
            batch_job_definition=settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME,
            batch_container_overrides={
                "command": command,
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
    def submit_pending(cls) -> List[Self]:
        """
        Submits all saved PENDING jobs to AWS Batch.
        Updates each job instance's batch_job_id, state, and processing_at fields,
        and its associated dataset state.
        Saves the changes to the db on success.
        Returns all the submitted jobs.
        """
        submitted_jobs = []

        if jobs := Job.objects.filter(state=JobStates.PENDING):
            for job in jobs:
                if aws_job_id := batch.submit_job(job):
                    job.batch_job_id = aws_job_id
                    job.state = JobStates.PROCESSING
                    job.update_state_at(save=False)
                    submitted_jobs.append(job)

            cls.bulk_update_state(submitted_jobs)

        return submitted_jobs

    @classmethod
    def terminate_processing(cls, reason: str | None = "Terminated processing jobs") -> List[Self]:
        """
        Terminates all processing, incomplete jobs on AWS Batch.
        Updates each job's state and terminated_at with the given terminated reason.
        Returns all the terminated jobs.
        """
        terminated_jobs = []

        if jobs := cls.objects.filter(state=JobStates.PROCESSING):

            for job in jobs:
                if batch.terminate_job(job):
                    job.state = JobStates.TERMINATED
                    job.terminated_reason = reason
                    job.update_state_at(save=False)
                    terminated_jobs.append(job)

            cls.bulk_update_state(terminated_jobs)

        return terminated_jobs

    @classmethod
    def bulk_update_state(cls, synced_jobs: List[Self]) -> None:
        """
        Updates the states of the synced jobs and their associated datasets.
        """
        updated_attrs = [
            "state",
            "processing_at",
            "succeeded_at",
            "failed_at",
            "failed_reason",
            "terminated_at",
            "terminated_reason",
        ]
        cls.objects.bulk_update(synced_jobs, updated_attrs)

        Dataset.update_from_last_jobs([job.dataset for job in synced_jobs])

    @classmethod
    def bulk_sync_state(cls) -> bool:
        """
        Syncs all processing jobs' states with the remote AWS Batch job statuses.
        Saves each job and its associated dataset if the state changes.
        """
        processing_jobs = cls.objects.filter(state=JobStates.PROCESSING)

        if not processing_jobs.exists():
            return False

        fetched_jobs = batch.get_jobs(processing_jobs)

        if not fetched_jobs:
            return False

        # Map the fetched AWS jobs for easy lookup by batch_job_id
        aws_jobs = {job["jobId"]: job for job in fetched_jobs}

        synced_jobs = []

        for job in processing_jobs:
            if aws_job := aws_jobs.get(job.batch_job_id):
                new_state, failed_reason = cls.get_job_state(aws_job)

                if new_state != job.state:
                    job.state = new_state
                    job.failed_reason = failed_reason
                    job.update_state_at(save=False)
                    synced_jobs.append(job)

        if not synced_jobs:
            return False

        cls.bulk_update_state(synced_jobs)
        return True

    def update_state_at(self, save: bool = True) -> None:
        """
        Updates timestamp fields, *_at, based on the latest job state.
        Make sure to set 'save' to False when calling this from bulk update methods
        or from instance methods that call save() within.
        """
        timestamp = make_aware(datetime.now())

        match self.state:
            case JobStates.PROCESSING:
                self.processing_at = timestamp
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
        Submits the unsaved PENDING job to AWS Batch.
        Updates batch_job_id, state, and processing_at fields,
        and its associated dataset state.
        Saves the changes to the db on success.
        """
        if self.state is not JobStates.PENDING:
            return False

        job_id = batch.submit_job(self)

        if not job_id:
            return False

        self.batch_job_id = job_id
        self.state = JobStates.PROCESSING
        self.update_state_at(save=False)

        self.save()  # Save this instance before bulk updating fields
        Job.bulk_update_state([self])

        return True

    def sync_state(self) -> bool:
        if self.state is not JobStates.PROCESSING:
            return False

        aws_jobs = batch.get_jobs([self])

        if not aws_jobs:
            return False

        new_state, failed_reason = self.get_job_state(aws_jobs[0])

        if new_state == self.state:
            return False

        self.state = new_state
        self.failed_reason = failed_reason
        self.update_state_at(save=False)

        Job.bulk_update_state([self])

        return True

    def terminate(self, reason: str | None = "Terminated processing job") -> bool:
        """
        Terminates the processing, incomplete job on AWS Batch.
        Updates state and terminated_at with the given terminated reason.
        """
        if self.state in common.FINAL_JOB_STATES:
            return self.state == JobStates.TERMINATED

        if not batch.terminate_job(self):
            return False

        self.state = JobStates.TERMINATED
        self.terminated_reason = reason
        self.update_state_at(save=False)

        Job.bulk_update_state([self])

        return True

    def get_retry_job(self) -> Self | bool:
        """
        Prepares a new Job instance for retry.
        Returns newly instantiated jobs.
        """
        if self.state not in common.FINAL_JOB_STATES:
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
