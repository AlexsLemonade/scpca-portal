from django.conf import settings
from django.template.loader import render_to_string

import boto3

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "emails"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "default.html"


def send_project_files_completed_email(
    project_id: str,
    sender: str = settings.EMAIL_SENDER,
    recipient: str = settings.TEST_EMAIL_RECIPIENT,
) -> None:
    SENDER = sender
    RECIPIENT = recipient
    CHARSET = "UTF-8"

    SUBJECT = f"All files generated for {project_id}"
    BODY_TEXT = (
        "Hot off the presses:\n\n"
        f"All files have been generated for project {project_id}"
        + "\n\nLove!,\nThe ScPCA Portal Team"
    )
    BODY_HTML = render_to_string(TEMPLATE_FILE_PATH, context={"project_id": project_id})

    ses = boto3.client("ses", region_name=settings.AWS_REGION)
    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": SUBJECT, "Charset": CHARSET},
            "Body": {
                "Text": {"Data": BODY_TEXT, "Charset": CHARSET},
                "Html": {"Data": BODY_HTML, "Charset": CHARSET},
            },
        },
    )


def send_dataset_file_completed_email(job: Job) -> None:
    SENDER = settings.EMAIL_SENDER
    RECIPIENT = job.dataset.email
    CHARSET = "UTF-8"

    SUBJECT = f"All files generated for {job.dataset.id}"
    BODY_TEXT = (
        "Hot off the presses:\n\n"
        f"All files have been generated for project {job.dataset.id}"
        + "\n\nLove!,\nThe ScPCA Portal Team"
    )
    BODY_HTML = render_to_string(TEMPLATE_FILE_PATH, context={"dataset_id": job.dataset.id})

    ses = boto3.client("ses", region_name=settings.AWS_REGION)
    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": SUBJECT, "Charset": CHARSET},
            "Body": {
                "Text": {"Data": BODY_TEXT, "Charset": CHARSET},
                "Html": {"Data": BODY_HTML, "Charset": CHARSET},
            },
        },
    )
