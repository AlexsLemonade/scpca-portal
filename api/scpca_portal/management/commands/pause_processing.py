import logging

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.models import Job

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """Pauses all processing jobs and adds them to the pending queue."""

    def handle(self, *args, **kwargs):
        self.pause_processing()

    def pause_processing(self):
        terminated_jobs = Job.terminate_processing(reason="Processing paused on re-deploy.")
        retry_jobs = Job.create_retry_jobs(terminated_jobs)

        retry_job_count = len(retry_jobs)
        logger.info(
            f"{retry_job_count} processing job{pluralize(retry_job_count)} were paused "
            "and added to the pending queue before deploy."
        )
