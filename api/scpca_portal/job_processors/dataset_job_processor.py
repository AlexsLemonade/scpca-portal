from scpca_portal import notifications, s3, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import JobStates
from scpca_portal.exceptions import DatasetLockedProjectError, DatasetMissingLibrariesError
from scpca_portal.job_processors import JobProcessorABC
from scpca_portal.models import ComputedFile

logger = get_and_configure_logger(__name__)


class DatasetJobProcessor(JobProcessorABC):

    steps = [
        "setup_work_dir",
        "purge_old_computed_file",
        "create_new_computed_file",
        "upload_new_computed_file",
        "clean_up_local_computed_file",
        "send_notification",
    ]

    exception_handlers = {
        ("create_new_computed_file", DatasetLockedProjectError): "handle_locked_project",
        ("create_new_computed_file", DatasetMissingLibrariesError): "handle_missing_libraries",
    }

    # Logging
    def on_run(self):
        logger.info(f"Processing {self.job.id} - {self.job.batch_job_id} - {self.job.dataset}")

    def on_step_start(self, step: str):
        logger.info(f"Entering step: {step}")

    def on_step_exception(self, step: str, e: Exception):
        logger.info(f"Handling step {step} exception {e.__class__.__name__}")
        logger.exception(e)

    def on_uncaught_exception(self, step, e: Exception):
        logger.info("Encountered uncaught exception.")
        logger.exception(e)
        self.job.save()
        self.job.dataset.save()
        if self.job.dataset.email:
            logger.info("Sending dataset job error email.")
            notifications.send_dataset_job_error_email(self.job)

    def on_run_done(self):
        self.job.save()
        self.job.dataset.save()
        logger.info("Job completed.")

    # Steps
    def setup_work_dir(self):
        utils.create_data_dirs()

    def purge_old_computed_file(self):
        if self.job.dataset.computed_file:
            self.job.dataset.comptued_file.purge(delete_from_s3=True)

    def create_new_computed_file(self):
        self.job.dataset.computed_file = ComputedFile.get_dataset_file(self.job.dataset)
        self.job.dataset.computed_file.save()
        self.job.dataset.save()

    def handle_locked_project(self, step: str, e: Exception):
        self.job.apply_state(JobStates.FAILED, reason="Dataset contains locked project.")
        self.job.save()
        self.job.dataset.save()
        self.job.create_retry_job()

    def handle_missing_libraries(self, step: str, e: Exception):
        self.job.apply_state(JobStates.FAILED, reason="Dataset contains missing libraries.")
        self.job.save()
        self.job.dataset.save()
        if self.job.dataset.email:
            logger.info("Sending dataset job error email.")
            notifications.send_dataset_job_error_email(self.job)

    def upload_new_computed_file(self):
        s3.upload_output_file(
            self.job.dataset.computed_file.s3_key, self.job.dataset.computed_file.s3_bucket
        )

    def clean_up_local_computed_file(self):
        self.job.dataset.computed_file.clean_up_local_computed_file()

    def send_notification(self):
        if self.job.dataset.email:
            notifications.send_dataset_job_success_email(self.job)
