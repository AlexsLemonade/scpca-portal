from django.db.models import TextChoices


class JobStates(TextChoices):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"
