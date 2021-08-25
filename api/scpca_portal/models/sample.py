from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.project import Project
from scpca_portal.models.project_summary import ProjectSummary


class Sample(SafeDeleteModel):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at", "id"]

    objects = SafeDeleteManager()
    deleted_objects = SafeDeleteDeletedManager()
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    has_cite_seq_data = models.BooleanField(default=False)
    scpca_sample_id = models.TextField(null=False)
    technologies = models.TextField(null=False)
    diagnosis = models.TextField(blank=True, null=True)
    subdiagnosis = models.TextField(blank=True, null=True)
    age_at_diagnosis = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    tissue_location = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    seq_units = models.TextField(blank=True, null=True)

    additional_metadata = JSONField(default=dict)

    project = models.ForeignKey(
        Project, null=False, on_delete=models.CASCADE, related_name="samples"
    )

    computed_file = models.OneToOneField(
        ComputedFile, blank=False, null=True, on_delete=models.CASCADE, related_name="sample"
    )

    is_deleted = models.BooleanField(default=False)


@receiver(post_save, sender="scpca_portal.Sample")
def update_project_counts(sender, instance=None, created=False, update_fields=None, **kwargs):
    """The Project and ProjectSummary models cache aggregated sample metadata.

    When Samples are added to the Project, we need to update these."""
    if not instance:
        # Nothing to do
        return

    project = instance.project

    diagnoses = set()
    seq_units = set()
    technologies = set()
    disease_timings = set()
    summaries = {}
    for sample in project.samples.all():
        diagnoses.add(sample.diagnosis)
        disease_timings.add(sample.disease_timing)
        sample_seq_units = sample.seq_units.split(",")
        sample_technologies = sample.technologies.split(",")
        seq_units = seq_units.union(set(sample_seq_units))
        technologies = technologies.union(set(sample_technologies))

        for seq_unit in sample_seq_units:
            for technology in sample_technologies:
                try:
                    summaries[(sample.diagnosis, seq_unit, technology)] += 1
                except KeyError:
                    summaries[(sample.diagnosis, seq_unit, technology)] = 1

    project.diagnoses = ", ".join(list(diagnoses))
    project.seq_units = ", ".join(list(seq_units))
    project.technologies = ", ".join(list(technologies))
    project.disease_timings = ", ".join(list(disease_timings))
    project.save()

    for summary, count in summaries.items():
        try:
            project_summary = ProjectSummary.objects.get(
                diagnosis=summary[0], seq_unit=summary[1], technology=summary[2]
            )
            project_summary.sample_count = count
        except ProjectSummary.DoesNotExist:
            ProjectSummary.objects.create(
                diagnosis=summary[0],
                seq_unit=summary[1],
                technology=summary[2],
                sample_count=count,
            )
