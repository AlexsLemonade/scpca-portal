class FileFormats:
    ANN_DATA = "ANN_DATA"
    SINGLE_CELL_EXPERIMENT = "SINGLE_CELL_EXPERIMENT"
    METADATA = "METADATA"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    CHOICES = (
        (ANN_DATA, "AnnData"),
        (SINGLE_CELL_EXPERIMENT, "Single cell experiment"),
        (METADATA, "Metadata"),
        (SUPPLEMENTARY, "Supplementary"),
    )
