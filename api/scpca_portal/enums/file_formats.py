from django.db.models import TextChoices


class FileFormats(TextChoices):
    SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT", "Single-cell experiment"
    ANN_DATA = "ANN_DATA", "AnnData"
    SPATIAL_SPACERANGER = "SPATIAL_SPACERANGER", "Spatial Spaceranger"
    METADATA = "METADATA", "Metadata"
    SUPPLEMENTARY = "SUPPLEMENTARY", "Supplementary"
