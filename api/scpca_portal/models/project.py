from django.db import models

from scpca_portal.models.computed_file import ComputedFile


class Project(models.Model):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scpca_id = models.TextField(unique=True, null=False)
    pi_name = models.TextField(null=False)
    human_readable_pi_name = models.TextField(null=False)
    title = models.TextField(null=False)
    abstract = models.TextField(null=False)
    contact_name = models.TextField(null=True)
    contact_email = models.TextField(null=True)
    has_bulk_rna_seq = models.BooleanField(default=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    disease_timings = models.TextField(null=False)
    diagnoses = models.TextField(blank=True, null=True)
    diagnoses_counts = models.TextField(blank=True, null=True)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    modalities = models.TextField(blank=True, null=True)

    additional_metadata_keys = models.TextField(blank=True, null=True)

    sample_count = models.IntegerField(default=0)

    computed_file = models.OneToOneField(
        ComputedFile, blank=False, null=True, on_delete=models.CASCADE, related_name="project"
    )
