from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3

from scpca_portal.config.logging import get_and_configure_logger

batch = boto3.client(
    "batch",
    region_name=settings.AWS_REGION,
)

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Dispatch send-test-email to Batch.
    """

    def add_arguments(self, parser):
        parser.add_argument("--sender", type=str, default=settings.EMAIL_SENDER)
        parser.add_argument("--recipient", type=str, default=settings.TEST_EMAIL_RECIPIENT)

    def handle(self, *args, **kwargs):
        self.dispatch_send_email(**kwargs)

    def dispatch_send_email(self, sender: str, recipient: str, **kwargs):
        command = [
            "python",
            "manage.py",
            "send_test_email",
        ]
        if sender:
            command.extend(["--sender", sender])
        if recipient:
            command.extend(["--recipient", recipient])

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        job_name = f"test-email_{timestamp}"

        response = batch.submit_job(
            jobName=job_name,
            jobQueue=settings.AWS_BATCH_FARGATE_JOB_QUEUE_NAME,
            jobDefinition=settings.AWS_BATCH_FARGATE_JOB_DEFINITION_NAME,
            containerOverrides={
                "command": command,
            },
        )

        logger.info(f'Job `{job_name}` submitted to Batch with jobId `{response["jobId"]}`')
