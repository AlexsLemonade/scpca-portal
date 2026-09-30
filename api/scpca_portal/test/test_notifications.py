from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from scpca_portal import notifications


class TestNotifications(TestCase):

    @patch("boto3.client")
    def test_send_email(self, mock_boto_client):
        mock_ses_client = MagicMock()
        mock_boto_client.return_value = mock_ses_client

        notifications.send_email(
            recipient="user@example.com",
            subject="Mock Subject",
            body_text="Mock body text",
            body_html="Mock body html",
        )

        mock_ses_client.send_email.assert_called_once_with(
            Source=settings.EMAIL_SENDER,
            Destination={
                "ToAddresses": ["user@example.com"],
                "BccAddresses": [],
            },
            Message={
                "Subject": {"Data": "Mock Subject", "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": "Mock body text", "Charset": "UTF-8"},
                    "Html": {"Data": "Mock body html", "Charset": "UTF-8"},
                },
            },
        )

    @patch("scpca_portal.notifications.send_email")
    @patch("scpca_portal.notifications.render_to_string")
    def test_send_templated_email(self, mock_render_to_string, mock_send_email):
        mock_render_to_string.side_effect = ["Mock body text", "Mock body html"]
        context = {"dataset": "Mock dataset"}

        notifications.send_templated_email(
            recipient="user@example.com",
            subject="Mock Subject",
            context=context,
            text_template="mock_text_template.txt",
            html_template="mock_text_template.html",
        )

        self.assertEqual(mock_render_to_string.call_count, 2)

        mock_render_to_string.assert_any_call(
            notifications.TEMPLATE_ROOT / "mock_text_template.txt",
            context={**context, **notifications.SHARED_TEMPLATE_CONTEXT},
        )

        mock_render_to_string.assert_any_call(
            notifications.TEMPLATE_ROOT / "mock_text_template.html",
            context={**context, **notifications.SHARED_TEMPLATE_CONTEXT},
        )

        mock_send_email.assert_called_once_with(
            "user@example.com",
            "Mock Subject",
            "Mock body text",
            "Mock body html",
            bcc_addresses=[settings.SLACK_NOTIFICATIONS_EMAIL],
        )

    @patch("scpca_portal.notifications.send_email")
    def test_send_slack_notification(self, mock_send_email):
        notifications.send_slack_notification(subject="Mock Subject", body="Mock body")

        mock_send_email.assert_called_once_with(
            settings.SLACK_NOTIFICATIONS_EMAIL, "Mock Subject", "Mock body", "Mock body"
        )
