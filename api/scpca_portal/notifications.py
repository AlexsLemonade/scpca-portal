from django.conf import settings
from django.template.loader import render_to_string

import boto3

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job

logger = get_and_configure_logger(__name__)

TEMPLATE_ROOT = settings.TEMPLATE_PATH / "emails"

SHARED_TEMPLATE_CONTEXT = {
    "domain": settings.DOMAIN,
    "contact_email": settings.EMAIL_CONTACT_ADDRESS,
}


def send_email(
    recipient: str,
    subject: str,
    body_text: str,
    body_html: str,
    sender: str = settings.EMAIL_SENDER,
):
    ses = boto3.client("ses", region_name=settings.AWS_REGION)

    bcc_addressses = [settings.SLACK_NOTIFICATIONS_EMAIL]
    # dont double send emails to slack
    if settings.SLACK_NOTIFICATIONS_EMAIL is recipient:
        bcc_addressses = []

    ses.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient], "BccAddresses": bcc_addressses},
        Message={
            "Subject": {"Data": subject, "Charset": settings.EMAIL_CHARSET},
            "Body": {
                "Text": {"Data": body_text, "Charset": settings.EMAIL_CHARSET},
                "Html": {"Data": body_html, "Charset": settings.EMAIL_CHARSET},
            },
        },
    )


def send_dataset_job_success_email(job: Job) -> None:
    subject = "Your ScPCA dataset is ready!"

    text_template = TEMPLATE_ROOT / "dataset_job_success.txt"
    body_text = render_to_string(
        text_template, context={"dataset": job.dataset, **SHARED_TEMPLATE_CONTEXT}
    )

    html_template = TEMPLATE_ROOT / "dataset_job_success.html"
    body_html = render_to_string(
        html_template, context={"dataset": job.dataset, **SHARED_TEMPLATE_CONTEXT}
    )

    return send_email(job.dataset.email, subject, body_text, body_html)


def send_dataset_job_error_email(job: Job) -> None:
    subject = "We were unable to process your dataset"

    text_template = TEMPLATE_ROOT / "dataset_job_error.txt"
    body_text = render_to_string(
        text_template, context={"dataset": job.dataset, **SHARED_TEMPLATE_CONTEXT}
    )

    html_template = TEMPLATE_ROOT / "dataset_job_error.html"
    body_html = render_to_string(
        html_template, context={"dataset": job.dataset, **SHARED_TEMPLATE_CONTEXT}
    )

    return send_email(job.dataset.email, subject, body_text, body_html)


# TODO: Remove this is just for computed files
def send_project_files_completed_email(project_id: str) -> None:
    subject = f"All files generated for {project_id}"
    body_text = f"All files have been generated for project {project_id}"

    return send_email(settings.SLACK_NOTIFICATIONS_EMAIL, subject, body_text, body_text)
