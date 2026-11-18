from django.db.models import TextChoices


class EventResources(TextChoices):
    DATASET = "DATASET", "dataset"
