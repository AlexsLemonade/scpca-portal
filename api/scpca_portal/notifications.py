from pathlib import Path

from django.conf import settings

import boto3

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)
ses = boto3.client("ses", region_name=settings.AWS_REGION)


def send_job_completed_email(resource_id: str, download_config_name: str) -> None:
    SENDER = ""
    RECIPIENT = ""
    CHARSET = "UTF-8"

    SUBJECT = f"Job Completed: `{resource_id} - {download_config_name}`"
    BODY_TEXT = (
        "Hot off the presses:\n\n"
        + f"Job is completed for {resource_id} - {download_config_name}"
        + "\n\nLove!,\nThe ScPCA Portal Team"
    )
    BODY_HTML = Path("email_templates/default.html").read_text().replace("\n", "")

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
