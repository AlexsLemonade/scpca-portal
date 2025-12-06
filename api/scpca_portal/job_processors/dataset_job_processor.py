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
        "remove_old_computed_file",
        "process_dataset",
        "upload_dataset",
        "clean_up_local",
        "send_notification",
    ]

    exception_handlers = {
        ("process_dataset", DatasetLockedProjectError): "handle_locked_project",
        ("process_dataset", DatasetMissingLibrariesError): "handle_missing_libraries",
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

    def on_run_done(self):
        logger.info("Job completed.")

    # Steps
    def setup_work_dir(self):
        utils.create_data_dirs()

    def remove_old_dataset(self):
        if self.job.dataset.computed_file:
            self.job.dataset.comptued_file.purge(self.update_s3)

    def process_dataset(self):
        self.job.dataset.computed_file = ComputedFile.get_dataset_file(self.job.dataset)
        self.job.dataset.save()

    def handle_locked_project(self, step: str, e: Exception):
        self.job.apply_state(JobStates.FAILED, reason="Dataset contains locked project.")
        self.job.save()
        self.job.create_retry_job()

    def handle_missing_libraries(self, step: str, e: Exception):
        self.job.apply_state(JobStates.FAILED, reason="Dataset contains missing libraries.")
        self.job.save()
        # TODO: Add failure notification

    def upload_dataset(self):
        s3.upload_output_file(self.computed_file.s3_key, self.computed_file.s3_bucket)

    def clean_up_local(self):
        self.computed_file.clean_up_local_computed_file()

    def send_notification(self):
        if self.job.dataset.email:
            notifications.send_dataset_file_completed_email(self.job)

    # End Steps
