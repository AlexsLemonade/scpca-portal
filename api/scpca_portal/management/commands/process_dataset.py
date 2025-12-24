from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.job_processors import DatasetJobProcessor
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    This command is meant to be called as an entrypoint to a AWS Batch job instance.
    Individual files are computed according to their passed dataset.

    Processing details can be found in: scpca_portal.job_processors.DatasetJobProcessor
    """

    def add_arguments(self, parser):
        parser.add_argument("--job-id", type=str)

    def handle(self, *args, **kwargs):
        self.process_dataset(**kwargs)

    def process_dataset(self, job_id: str, **kwargs) -> None:
        job = Job.objects.get(id=job_id)
        processor = DatasetJobProcessor(job)
        processor.run()
