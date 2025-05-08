from django.db.models import TextChoices


class FileFormats(TextChoices):
    ANN_DATA = "ANN_DATA"
    SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"
    METADATA = "METADATA"
    SUPPLEMENTARY = "SUPPLEMENTARY"
