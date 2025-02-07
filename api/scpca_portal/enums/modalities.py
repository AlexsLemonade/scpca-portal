class Modalities:
    BULK_RNA_SEQ = "BULK_RNA_SEQ"
    CITE_SEQ = "CITE_SEQ"
    MULTIPLEXED = "MULTIPLEXED"
    SINGLE_CELL = "SINGLE_CELL"
    SPATIAL = "SPATIAL"

    CHOICES = (
        (SINGLE_CELL, "Single Cell"),
        (SPATIAL, "Spatial"),
    )

    NAME_MAPPING = {
        BULK_RNA_SEQ: "Bulk RNA-seq",
        CITE_SEQ: "CITE-seq",
        MULTIPLEXED: "Multiplexed",
        SPATIAL: "Spatial Data",
    }
