from django.conf import settings
from django.template.loader import render_to_string

import boto3

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
ses = boto3.client("ses", region_name=settings.AWS_REGION)

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "email_templates"
TEMPLATE_FILE_PATH = TEMPLATE_ROOT / "default.html"


def send_project_files_completed_email(
    project_id: str,
    sender: str = settings.TEST_EMAIL_SENDER,
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
