from django.db.models import TextChoices


class LoadableResourceStates(TextChoices):
    LOCKED = "LOCKED"
    NEW = "NEW"
    TAINTED = "TAINTED"
    SYNCED = "SYNCED"
