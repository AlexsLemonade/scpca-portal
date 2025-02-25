from django.db.models import TextChoices


class Modalities(TextChoices):
    BULK_RNA_SEQ = "BULK_RNA_SEQ", "Bulk RNA-seq"
    CITE_SEQ = "CITE_SEQ", "CITE-seq"
    MULTIPLEXED = "MULTIPLEXED", "Multiplexed"
    SINGLE_CELL = "SINGLE_CELL", "Single Cell"
    SPATIAL = "SPATIAL", "Spatial Data"
