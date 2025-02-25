from django.db.models import TextChoices


class Modalities(TextChoices):
    BULK_RNA_SEQ = "BULK_RNA_SEQ"
    CITE_SEQ = "CITE_SEQ"
    MULTIPLEXED = "MULTIPLEXED"
    SINGLE_CELL = "SINGLE_CELL"
    SPATIAL = "SPATIAL"
