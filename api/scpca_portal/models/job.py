from datetime import datetime
from typing import List

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import batch, common, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import JobStates
from scpca_portal.exceptions import (
    DatasetError,
    DatasetLockedProjectError,
    JobError,
    JobInvalidRetryStateError,
    JobInvalidTerminateStateError,
    JobSubmissionFailedError,
    JobSubmitNotPendingError,
    JobSyncNotProcessingError,
    JobSyncStateFailedError,
    JobTerminationFailedError,
)
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.dataset import Dataset

logger = get_and_configure_logger(__name__)


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

    # INSTANCE CREATIONAL LOGIC
    @classmethod
    def get_dataset_job(cls, dataset: Dataset) -> Self:
        """
        Prepare a Job instance for a dataset without saving it to the db.
        """
        return cls(
            batch_job_name=str(dataset.id),
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

    def create_retry_job(self, *, save: bool = True) -> Self:
        """
        Prepares a new PENDING job for retry with:
        - incremented attempt count
        - batch fields
        - the associated dataset
        By default, saves the new job as PENDING (state, timestamp).
        (For bulk operations, the caller should pass False to prevent saving.)
        Calls the dataset's method to sync the job's state.
        Raises an error when unable to create a retry job:
        - JobInvalidRetryStateError
        Returns the new job, or False if the current job is not in a final state.
        """
        if self.state not in common.FINAL_JOB_STATES:
            raise JobInvalidRetryStateError(self)

        new_job = Job(
            attempt=self.attempt + 1,
            batch_job_name=self.batch_job_name,
            batch_job_definition=self.batch_job_definition,
            batch_job_queue=self.batch_job_queue,
            batch_container_overrides=self.batch_container_overrides,
            dataset=self.dataset,
        )

        new_job.apply_state(JobStates.PENDING)
        if save:
            new_job.save()
            if new_job.dataset:  # TODO: Remove after the dataset release
                new_job.dataset.save()

        return new_job

    @classmethod
    def create_retry_jobs(cls, jobs: List[Self]) -> List[Self]:
        """
        Creates new PENDING jobs to retry the given jobs.
        Calls the datasets' method to sync the jobs' state.
        Returns the newly created retry jobs.
        """
        if not jobs:
            return []

        retry_jobs = []
        retry_datasets = []

        for job in jobs:
            if retry_job := job.create_retry_job(save=False):
                retry_jobs.append(retry_job)
                if job.dataset:  # TODO: Remove after the dataset release
                    retry_datasets.append(job.dataset)

        if retry_jobs:
            cls.objects.bulk_create(retry_jobs)
            if retry_datasets:  # TODO: Remove after the dataset release
                Dataset.bulk_update_state(retry_datasets)

        return retry_jobs

    # STATE LOGIC
    def apply_state(self, state: JobStates, reason: str | None = None) -> bool:
        """
        Sets the job's state, timestamp, and reason.
        Calls the dataset's method to sync the job's state.
        Returns a boolean indicating if the caller should save updates.
        """
        if self.state == state:
            return False

        self.state = state
        state_str = state.lower()
        setattr(self, f"{state_str}_at", make_aware(datetime.now()))
        if hasattr(self, f"{state_str}_reason"):
            setattr(self, f"{state_str}_reason", reason)

        if self.dataset:
            self.dataset.apply_job_state(self)  # Sync the dataset state

        return True

    @classmethod
    def bulk_update_state(cls, jobs: List[Self]) -> None:
        """
        Updates state attributes of the given jobs in bulk.
        """
        STATE_UPDATE_ATTRS = [
            "state",
            "processing_at",
            "succeeded_at",
            "failed_at",
            "failed_reason",
            "terminated_at",
            "terminated_reason",
        ]
        cls.objects.bulk_update(jobs, STATE_UPDATE_ATTRS)

    @classmethod
    def bulk_sync_state(cls) -> bool:
        """
        Syncs all PROCESSING jobs' states with the corresponding AWS Batch jobs.
        Saves the jobs (state, timestamp, reason).
        Calls the datasets' method to sync the jobs' state.
        Returns a boolean indicating if the jobs and datasets were updated during sync.
        """
        processing_jobs = cls.objects.filter(state=JobStates.PROCESSING)
        if not processing_jobs.exists():
            return False

        synced_jobs = []
        synced_datasets = []
        failed_job_ids = []

        fetched_jobs = []
        try:
            fetched_jobs = batch.get_jobs(processing_jobs)
        except Exception:
            failed_job_ids.extend(processing_jobs)

        # Map the fetched AWS jobs for easy lookup by batch_job_id
        aws_jobs = {job["jobId"]: job for job in fetched_jobs}

        for job in processing_jobs:
            if aws_job := aws_jobs.get(job.batch_job_id):
                new_state, reason = cls.get_job_state(aws_job)
                if job.apply_state(new_state, reason):
                    synced_jobs.append(job)
                    if job.dataset:  # TODO: Remove after the dataset release
                        synced_datasets.append(job.dataset)

        if not synced_jobs:
            logger.info("No jobs were updated during sync.")
            return False

        logger.info(f"Synced {len(synced_jobs)} jobs with AWS.")
        cls.bulk_update_state(synced_jobs)
        if synced_datasets:  # TODO: Remove after the dataset release
            Dataset.bulk_update_state(synced_datasets)

        if failed_job_ids:
            logger.info(f"{len(failed_job_ids)} jobs failed to sync.")

        return True

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

    def sync_state(self) -> bool:
        """
        Syncs the job state with the AWS Batch status.
        Saves the job if the state has changed (state, timestamp, reason).
        Calls the dataset's method to sync the job's state.
        Raises an error when unable to sync:
        - JobSyncNotProcessingError
        - JobSyncStateFailedError
        Returns a boolean indicating if the job and dataset were changed during sync.
        """
        if self.state is not JobStates.PROCESSING:
            raise JobSyncNotProcessingError(self)

        try:
            aws_jobs = batch.get_jobs([self])
        except Exception as error:
            raise JobSyncStateFailedError(self) from error

        new_state, reason = self.get_job_state(aws_jobs[0])

        if new_state == self.state:
            return False

        if self.apply_state(new_state, reason):
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

        return True

    # API SUBMISSION AND TERMINATION LOGIC
    def submit(self, *, save=True):
        """
        Submits the PENDING job to AWS Batch and assigns batch_job_id.
        By default, saves the job as PROCESSING (state, timestamp).
        (For bulk operations, the caller should pass False to prevent saving.)
        Calls the dataset's method to sync the job's state.
        Raises an error when unable to submit:
        - JobSubmitNotPendingError
        - DatasetLockedProjectError
        - JobSubmissionFailedError
        """
        if self.state != JobStates.PENDING:
            raise JobSubmitNotPendingError(self)

        # if job has dataset, dynamically configure job for submission
        if self.dataset:
            if self.dataset.is_locked:
                raise DatasetLockedProjectError(self.dataset)

            # dynamically choose queue based on dataset size
            self.batch_job_queue = settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME
            self.batch_job_definition = settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
            if self.dataset.estimated_size_in_bytes > Job.MAX_FARGATE_SIZE_IN_BYTES:
                self.batch_job_queue = settings.AWS_BATCH_EC2_JOB_QUEUE_NAME
                self.batch_job_definition = settings.AWS_BATCH_EC2_JOB_DEFINITION_NAME

            # Save job to get ID before submitting
            if not self.id:
                self.save()

            self.batch_container_overrides = {
                "command": [
                    "python",
                    "manage.py",
                    "process_dataset",
                    "--job-id",
                    str(self.id),
                ],
            }

        job_id = batch.submit_job(self)

        if not job_id:
            raise JobSubmissionFailedError(self)

        self.batch_job_id = job_id
        self.apply_state(JobStates.PROCESSING)

        if save:
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

    def increment_attempt_or_fail(self) -> bool:
        """
        Increment a job's attempt count.
        If attempts exceed the max allotted job attempts, fail the job.
        """
        if self.attempt >= common.MAX_JOB_ATTEMPTS:
            self.apply_state(JobStates.FAILED, "Unable to dispatch job to aws")
            self.save()
            return False

        self.attempt += 1
        self.save()
        return True

    @classmethod
    def submit_pending(cls) -> List[Self]:
        """
        Submits all PENDING jobs to AWS Batch.
        Updates the jobs' batch_job_id and saves them as PROCESSING (state, timestamp).
        Calls the datasets' method to sync the jobs' state.
        Returns all the submitted jobs.
        """
        submitted_jobs = []
        submitted_datasets = []
        pending_jobs = []
        failed_jobs = []

        for job in Job.objects.filter(state=JobStates.PENDING):
            try:
                job.submit(save=False)
                submitted_jobs.append(job)
                if job.dataset:  # TODO: Remove after the dataset release
                    submitted_datasets.append(job.dataset)
            except (JobError, DatasetError):
                if job.increment_attempt_or_fail():
                    pending_jobs.append(job)
                else:
                    failed_jobs.append(job)

        if submitted_jobs:
            logger.info(f"Submitted {len(submitted_jobs)} jobs to AWS.")
            cls.bulk_update_state(submitted_jobs)
            if submitted_datasets:  # TODO: Remove after the dataset release
                Dataset.bulk_update_state(submitted_datasets)

        if pending_jobs:
            logger.info(f"{len(pending_jobs)} jobs were not submitted but are still pending.")
        if failed_jobs:
            logger.info(f"{len(failed_jobs)} jobs failed to submit.")

        return submitted_jobs

    def terminate(self, reason: str | None = "Terminated processing job", *, save=True):
        """
        Terminates the PROCESSING job (incomplete) on AWS Batch.
        By default, saves the job as TERMINATED (state, timestamp, reason)
        Calls the dataset's method to sync the job's state.
        Raises an error when unable to terminate:
        - JobInvalidTerminateStateError
        - JobTerminationFailedError
        """
        if self.state in common.FINAL_JOB_STATES:
            raise JobInvalidTerminateStateError(self)

        if not batch.terminate_job(self):
            raise JobTerminationFailedError(self)

        self.apply_state(JobStates.TERMINATED, reason)

        if save:
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

    @classmethod
    def terminate_processing(cls, reason: str | None = "Terminated processing jobs") -> List[Self]:
        """
        Terminates all PROCESSING jobs (incomplete) on AWS Batch.
        Saves the jobs as TERMINATED (state, timestamp, reason).
        Calls the datasets' method to sync the jobs' state.
        Returns all the terminated jobs.
        """
        terminated_jobs = []
        terminated_datasets = []
        final_state_jobs = []
        failed_jobs = []

        for job in cls.objects.filter(state=JobStates.PROCESSING):
            try:
                job.terminate(reason=reason, save=False)
                terminated_jobs.append(job)
                if job.dataset:  # TODO: Remove after the dataset release
                    terminated_datasets.append(job.dataset)
            except JobInvalidTerminateStateError:
                final_state_jobs.append(job)
            except JobError:
                failed_jobs.append(job)

        if terminated_jobs:
            logger.info(f"Terminated {len(terminated_jobs)} jobs on AWS.")
            cls.bulk_update_state(terminated_jobs)
            if terminated_datasets:  # TODO: Remove after the dataset release
                Dataset.bulk_update_state(terminated_datasets)

        if final_state_jobs:
            logger.info(f"{len(final_state_jobs)} jobs were not in a terminable state.")
        if failed_jobs:
            logger.info(f"{len(failed_jobs)} jobs failed to terminate.")

        return terminated_jobs

    # BATCH PROCESSING LOGIC
    def process_dataset_job(
        self,
        update_s3: bool = True,
        clean_up_output_data=False,
    ) -> None:
        if old_dataset_file := self.dataset.computed_file:
            old_dataset_file.purge(update_s3)

        computed_file = ComputedFile.get_dataset_file(self.dataset)

        if update_s3:
            s3.upload_output_file(computed_file.s3_key, computed_file.s3_bucket)

        computed_file.save()
        self.dataset.computed_file = computed_file
        self.dataset.save()

        if clean_up_output_data:
            computed_file.clean_up_local_computed_file()
