from datetime import datetime
from typing import List

from django.conf import settings
from django.db import models
from django.utils.timezone import make_aware

from typing_extensions import Self

from scpca_portal import batch, common, s3
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import JobStates
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
    def get_dataset_job(cls, dataset: Dataset) -> Self:
        """
        Prepare a Job instance for a dataset without saving it to the db.
        """
        return cls(
            batch_job_name=str(dataset.id),
            dataset=dataset,
        )

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
            retry_jobs.append(job.get_retry_job(save=False))

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
        for job in Job.objects.filter(state=JobStates.PENDING):
            try:
                logger.info(f"Trying {job.dataset} job ({job.state}).")
                job.submit()
                submitted_jobs.append(job)
                logger.info(f"{job.dataset} job successfully dispatched.")
            except Exception:
                logger.info(f"{job.dataset} job (attempt {job.attempt}) is being requeued.")
                job.increment_attempt_or_fail()

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

        Dataset.update_from_last_jobs([job.dataset for job in synced_jobs if job.dataset])

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

    def increment_attempt_or_fail(self) -> None:
        """
        Increment a job's attempt count.
        If attempts exceed the max allotted job attempts, fail the job.
        """
        if self.attempt >= common.MAX_JOB_ATTEMPTS:
            self.apply_state(JobStates.FAILED, "Unable to dispatch job to aws")
        else:
            self.attempt += 1

        self.save()

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

        self.dataset.apply_job_state(self)  # Sync the dataset state
        return True

    # TODO: Remove obsolete code blocks related to old sync state flows
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
        Submits the PENDING job to AWS Batch and assigns batch_job_id.
        Saves the job as PROCESSING (state, timestamp).
        Calls the dataset's method to sync the job's state.
        Returns a boolean indicating if the job and dataset were updated and saved.
        """
        if self.state != JobStates.PENDING:
            raise Exception("Job not pending.")

        # if job has dataset, dynamically configure job and save before submitting
        if self.dataset:
            if self.dataset.has_lockfile_projects or self.dataset.has_locked_projects:
                raise Exception("Dataset has a locked project.")

            # dynamically choose queue based on dataset size
            self.batch_job_queue = settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME
            self.batch_job_definition = settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME
            if self.dataset.estimated_size_in_bytes > Job.MAX_FARGATE_SIZE_IN_BYTES:
                self.batch_job_queue = settings.AWS_BATCH_EC2_JOB_QUEUE_NAME
                self.batch_job_definition = settings.AWS_BATCH_EC2_JOB_DEFINITION_NAME

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

            self.save()

        job_id = batch.submit_job(self)

        if not job_id:
            raise Exception("Error submitting job to Batch.")

        self.batch_job_id = job_id

        if self.apply_state(JobStates.PROCESSING):
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

        return True

    def sync_state(self) -> bool:
        """
        Syncs the job state with the AWS Batch status.
        Saves the job if the state has changed (state, timestamp, reason).
        Calls the dataset's method to sync the job's state.
        Returns a boolean indicating if the job and dataset were updated and saved.
        """
        if self.state is not JobStates.PROCESSING:
            return False

        aws_jobs = batch.get_jobs([self])

        if not aws_jobs:
            return False

        new_state, reason = self.get_job_state(aws_jobs[0])

        if new_state == self.state:
            return False

        if self.apply_state(new_state, reason):
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

        return True

    def terminate(self, reason: str | None = "Terminated processing job") -> bool:
        """
        Terminates the PROCESSING job (incomplete) on AWS Batch.
        Save the job as TERMINATED (state, timestamp, reason)
        Calls the dataset's method to sync the job's state.
        Returns a boolean indicating if the job and dataset were updated and saved.
        """
        if self.state in common.FINAL_JOB_STATES:
            return self.state == JobStates.TERMINATED

        if not batch.terminate_job(self):
            return False

        if self.apply_state(JobStates.TERMINATED, reason):
            self.save()
            if self.dataset:  # TODO: Remove after the dataset release
                self.dataset.save()

        return True

    def get_retry_job(self, save: bool = True) -> Self | bool:
        """
        Prepares a new PENDING job for retry with:
        - incremented attempt count
        - batch fields
        - the associated dataset
        By default, saves the new job as PENDING (state, timestamp).
        (For bulk operations, the caller should pass False to prevent saving.)
        Calls the dataset's method to sync the job's state.
        Returns the new job, or False if the current job is not in a final state.
        """
        if self.state not in common.FINAL_JOB_STATES:
            return False

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
