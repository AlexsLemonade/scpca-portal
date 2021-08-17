from django.db import models

from scpca_portal.models.processor import Processor
from scpca_portal.models.sample import Sample


class SampleProcessorAssociation(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    sample = models.ForeignKey(Sample, blank=False, null=False, on_delete=models.CASCADE)
    processor = models.ForeignKey(Processor, blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        db_table = "sample_processor_associations"
        unique_together = ("sample", "processor")
