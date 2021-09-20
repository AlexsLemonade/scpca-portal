from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.project import Project
from scpca_portal.models.project_summary import ProjectSummary


class Sample(models.Model):
    class Meta:
        db_table = "samples"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scpca_id = models.TextField(unique=True, null=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
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


@receiver(post_save, sender="scpca_portal.Sample")
def update_project_counts(sender, instance=None, created=False, update_fields=None, **kwargs):
    """The Project and ProjectSummary models cache aggregated sample metadata.

    When Samples are added to the Project, we need to update these."""
    if not instance:
        # Nothing to do
        return

    project = instance.project

    additional_metadata_keys = set()
    diagnoses = set()
    seq_units = set()
    technologies = set()
    disease_timings = set()
    diagnoses_counts = {}
    summaries = {}
    has_cite_seq_data = False
    has_spatial_data = False
    for sample in project.samples.all():
        additional_metadata_keys.update(sample.additional_metadata.keys())
        diagnoses.add(sample.diagnosis)
        disease_timings.add(sample.disease_timing)
        sample_seq_units = sample.seq_units.split(",")
        sample_technologies = sample.technologies.split(",")
        seq_units = seq_units.union(set(sample_seq_units))
        technologies = technologies.union(set(sample_technologies))

        if sample.has_cite_seq_data:
            has_cite_seq_data = True

        if sample.has_spatial_data:
            has_cite_seq_data = True

        try:
            diagnoses_counts[sample.diagnosis] += 1
        except KeyError:
            diagnoses_counts[sample.diagnosis] = 1

        for seq_unit in sample_seq_units:
            for technology in sample_technologies:
                try:
                    summaries[(sample.diagnosis, seq_unit, technology)] += 1
                except KeyError:
                    summaries[(sample.diagnosis, seq_unit, technology)] = 1

    diagnoses_strings = []
    for diagnosis, count in diagnoses_counts.items():
        diagnoses_strings.append(f"{diagnoses} ({count})")

    modalities = []
    if has_cite_seq_data:
        modalities.append("CITE-seq")
    if has_spatial_data:
        modalities.append("Spatial Data")
    if project.has_bulk_rna_seq:
        modalities.append("Bulk RNA-seq")

    project.additional_metadata_keys = ", ".join(list(additional_metadata_keys))
    project.modalities = ", ".join(list(modalities))
    project.diagnoses_counts = ", ".join(list(diagnoses_strings))
    project.diagnoses = ", ".join(list(diagnoses))
    project.seq_units = ", ".join(list(seq_units))
    project.technologies = ", ".join(list(technologies))
    project.disease_timings = ", ".join(list(disease_timings))
    project.sample_count = project.samples.count()
    project.has_cite_seq_data = has_cite_seq_data
    project.has_spatial_data = has_spatial_data
    project.save()

    for summary, count in summaries.items():
        try:
            project_summary = ProjectSummary.objects.get(
                project=project, diagnosis=summary[0], seq_unit=summary[1], technology=summary[2]
            )
            project_summary.sample_count = count
        except ProjectSummary.DoesNotExist:
            ProjectSummary.objects.create(
                project=project,
                diagnosis=summary[0],
                seq_unit=summary[1],
                technology=summary[2],
                sample_count=count,
            )
