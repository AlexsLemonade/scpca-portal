from unittest.mock import ANY, MagicMock, patch

from django.conf import settings
from django.test import TestCase

from scpca_portal import notifications
from scpca_portal.enums import JobStates
from scpca_portal.test.factories import DatasetFactory, JobFactory


class TestNotifications(TestCase):

    @patch("boto3.client")
    def test_send_dataset_job_success_email(self, mock_boto_client):
        mock_ses_client = MagicMock()
        mock_boto_client.return_value = mock_ses_client
        mock_ses_client.send_email.return_value = {"MessageId": "mocked-message-id"}

        dataset_id = "b369f67f-69c8-46a9-8fcf-746f35fc7e74"
        job = JobFactory(state=JobStates.SUCCEEDED, dataset=DatasetFactory(id=dataset_id))

        notifications.send_dataset_job_success_email(job)
        mock_ses_client.send_email.assert_called_once_with(
            Source=settings.EMAIL_SENDER,
            Destination={
                "ToAddresses": [job.dataset.email],
                "BccAddresses": [settings.SLACK_NOTIFICATIONS_EMAIL],
            },
            Message={
                "Subject": {"Data": "Your ScPCA dataset is ready!", "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": ANY, "Charset": "UTF-8"},
                    "Html": {"Data": ANY, "Charset": "UTF-8"},
                },
            },
        )
