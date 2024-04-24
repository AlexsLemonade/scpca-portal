from django.db import models


class CommonDataAttributes(models.Model):
    """Common attributes for Project, Sample, and ComputedFile models."""

    class Meta:
        abstract = True

    has_bulk_rna_seq = models.BooleanField(default=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_multiplexed_data = models.BooleanField(default=False)


class TimestampedModel(models.Model):
    """Base model with auto created_at and updated_at fields."""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
