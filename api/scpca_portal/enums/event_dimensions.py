from django.db.models import TextChoices


class EventDimensions:
    class Dataset(TextChoices):
        RESOURCE_ID = "resource_id", "resource_id"
        FORMAT = "format", "format"
        INCLUDES_FILES_MERGED = "includes_files_merged", "includes_files_merged"
        HAS_PUBLICATIONS = "has_publications", "has_publications"
        BUTTON_NAME = "button_name", "button_name"
        PAGE_NAME = "page_name", "page_name"

    @classmethod
    def choices(cls):
        return [
            choice
            for enum in vars(cls).values()
            if isinstance(enum, type) and issubclass(enum, TextChoices)
            for choice in enum.choices
        ]
