from django.conf import settings
from django.template.loader import render_to_string

import boto3

from scpca_portal.config.logging import get_and_configure_logger

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
    *,
    bcc_addresses: list[str] | None = None,
    sender: str = settings.EMAIL_SENDER,
) -> None:
    if bcc_addresses is None:
        bcc_addresses = []

    ses = boto3.client("ses", region_name=settings.AWS_REGION)

    ses.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient], "BccAddresses": bcc_addresses},
        Message={
            "Subject": {"Data": subject, "Charset": settings.EMAIL_CHARSET},
            "Body": {
                "Text": {"Data": body_text, "Charset": settings.EMAIL_CHARSET},
                "Html": {"Data": body_html, "Charset": settings.EMAIL_CHARSET},
            },
        },
    )


def send_templated_email(
    recipient: str,
    subject: str,
    context: dict,
    text_template: str,
    html_template: str,
) -> None:
    context = {**context, **SHARED_TEMPLATE_CONTEXT}
    body_text = render_to_string(TEMPLATE_ROOT / text_template, context=context)
    body_html = render_to_string(TEMPLATE_ROOT / html_template, context=context)

    send_email(
        recipient, subject, body_text, body_html, bcc_addresses=[settings.SLACK_NOTIFICATIONS_EMAIL]
    )


def send_slack_notification(subject: str, body: str) -> None:
    send_email(settings.SLACK_NOTIFICATIONS_EMAIL, subject, body, body)
