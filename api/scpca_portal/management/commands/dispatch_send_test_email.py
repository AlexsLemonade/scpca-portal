import logging
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3

batch = boto3.client(
    "batch",
    region_name=settings.AWS_REGION,
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Dispatch send-test-email to Batch.
    """

    def add_arguments(self, parser):
        parser.add_arguments("--sender", type=str, default="engineering@ccdatalab.org")
        parser.add_arguments(
            "--recipient",
            type=str,
            default="ccdl-test-channel-aaaabmdgmewpi5ph2qohssfx54@alexslemonade.slack.com",
        )

    def handle(self, *args, **kwargs):
        self.dispatch_send_email(**kwargs)

    def dispatch_send_email(self, sender: str, recipient: str, **kwargs):
        sender_flag = f"--sender {sender}" if sender else ""
        recipient_flag = f"--recipient {recipient}" if recipient else ""
        job_name = f"Test email from {sender} - {str(datetime.now())}"

        response = batch.submit_job(
            jobName=job_name,
            jobQueue=settings.AWS_BATCH_JOB_QUEUE_NAME,
            jobDefinition=settings.AWS_BATCH_JOB_DEFINITION_NAME,
            containerOverrides={
                "command": [
                    "python",
                    "manage.py",
                    "send_test_email",
                    sender_flag,
                    recipient_flag,
                ],
            },
        )

        logger.info(f'{job_name} submitted to Batch with jobId {response["jobId"]}')
