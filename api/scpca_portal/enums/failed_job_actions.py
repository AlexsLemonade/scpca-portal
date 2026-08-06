from django.db.models import TextChoices


class FailedJobActions(TextChoices):
    EMAIL = "EMAIL"  # Send a dataset error email for unrecoverable error
    RETRY = "RETRY"  # Create a new retry job for recoverable error
    SLACK = "SLACK"  # Send a Slack notification to request manual error handling
