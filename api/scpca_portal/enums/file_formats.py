from django.db.models import TextChoices


class FileFormats(TextChoices):
    ANN_DATA = "ANN_DATA", "AnnData"
    SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT", "Single-cell experiment"
    METADATA = "METADATA", "Metadata"
    SUPPLEMENTARY = "SUPPLEMENTARY", "Supplementary"
