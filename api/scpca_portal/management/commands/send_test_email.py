from django.conf import settings
from django.core.management.base import BaseCommand

import boto3

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)

ses = boto3.client("ses", region_name=settings.AWS_REGION)


class Command(BaseCommand):
    help = """
    Send a test email from AWS SES.
    """

    def add_arguments(self, parser):
        parser.add_argument("--sender", type=str, default=settings.EMAIL_SENDER)
        parser.add_argument("--recipient", type=str, default=settings.TEST_EMAIL_RECIPIENT)

    def handle(self, *args, **kwargs):
        self.send_test_email(**kwargs)

    def send_test_email(self, sender: str, recipient: str, **kwargs):
        SENDER = sender
        RECIPIENT = recipient
        SUBJECT = "SES Test Email"
        CHARSET = "UTF-8"
        BODY_TEXT = (
            f"Hello, {recipient}\nThis is a test email sent from AWS SES.\nBest regards,\n{sender}"
        )
        BODY_HTML = f"""
        <html>
        <body>
            <h2>Hello, {recipient}</h2>
            <p>This is a test email sent from AWS SES.</p>
            <p>Best regards,</p>
            <p>{sender}</p>
        </body>
        </html>
        """

        response = ses.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [RECIPIENT]},
            Message={
                "Subject": {"Data": SUBJECT, "Charset": CHARSET},
                "Body": {"Text": {"Data": BODY_TEXT}, "Html": {"Data": BODY_HTML}},
            },
        )

        logger.info(f'Email sent successfully! Message ID: {response["MessageId"]}')
