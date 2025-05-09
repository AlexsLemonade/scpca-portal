from django.db.models import TextChoices


class JobStates(TextChoices):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"
