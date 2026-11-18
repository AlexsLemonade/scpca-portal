from django.db.models import TextChoices


class EventTypes:
    class Dataset(TextChoices):
        DOWNLOAD_CCDL_DATASET = "DOWNLOAD_CCDL_DATASET", "download_ccdl_dataset"
        pass

    @classmethod
    def choices(cls):
        return [
            choice
            for enum in vars(cls).values()
            if isinstance(enum, type) and issubclass(enum, TextChoices)
            for choice in enum.choices
        ]
