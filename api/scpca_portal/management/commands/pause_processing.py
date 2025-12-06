from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Pauses all processing jobs and adds them to the pending queue."""

    def handle(self, *args, **kwargs):
        self.pause_processing()

    def pause_processing(self):
        termination_reason = "Processing paused via pause_processing command."
        terminated_jobs = Job.terminate_processing(reason=termination_reason)

        retry_jobs = Job.create_retry_jobs(terminated_jobs)

        retry_job_count = len(retry_jobs)
        logger.info(
            f"{retry_job_count} processing job{pluralize(retry_job_count)} were paused "
            "and added to the pending queue."
        )
