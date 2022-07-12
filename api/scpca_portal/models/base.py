from django.db import models


class BulkModel(models.Model):
    """Base model for bulk create/update operations."""

    class Meta:
        abstract = True

    @classmethod
    def bulk_create(cls, entries):
        """
        Inserts the provided entries into the DB in an efficient manner.
        The model's save() method will not be called, and the `pre_save` and
        `post_save` signals will not be sent.
        It does not work with many-to-many relationships.
        Returns a list of created objects.

        See https://docs.djangoproject.com/en/4.0/ref/models/querysets/#bulk-create
        for more details.
        """

        return cls.objects.bulk_create(entries)


class TimestampedModel(models.Model):
    """Base model with auto created_at and updated_at fields."""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
