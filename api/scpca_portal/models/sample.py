from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from safedelete.managers import SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SOFT_DELETE, SafeDeleteModel

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
    technology = models.TextField(null=False)
    diagnosis = models.TextField(blank=True, null=True)
    subdiagnosis = models.TextField(blank=True, null=True)
    age_at_diagnosis = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    disease_timing = models.TextField(blank=True, null=True)
    has_spinal_leptomeningeal_mets = models.BooleanField(default=False)
    tissue_location = models.TextField(blank=True, null=True)
    braf_status = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    seq_unit = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)

    project = models.ForeignKey(
        Project, null=False, on_delete=models.CASCADE, related_name="samples"
    )

    processors = models.ManyToManyField("Processor", through="SampleProcessorAssociation")


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
    summaries = {}
    for sample in project.samples.all():
        diagnoses.add(sample.diagnosis)
        seq_units.add(sample.seq_unit)
        technologies.add(sample.technology)

        try:
            summaries[(sample.diagnosis, sample.seq_unit, sample.technology)] += 1
        except KeyError:
            summaries[(sample.diagnosis, sample.seq_unit, sample.technology)] = 1

    project.diagnoses = ", ".join(list(diagnoses))
    project.seq_units = ", ".join(list(seq_units))
    project.technologies = ", ".join(list(technologies))
    project.save()

    for summary, count in summaries.items():
        try:
            project_summary = ProjectSummary.objects.get(
                diagnosis=summary[0], seq_unit=summary[1], technology=summary[2]
            )
            project_summary.sample_count = count
        except ProjectSummary.DoesNotExist:
            ProjectSummary.objects.create(
                diagnosis=summary[0], seq_unit=summary[1], technology=summary[2], sample_count=count
            )
