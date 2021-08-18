"""This file houses serializers which can be used for nested relationships.

These serializers do not use nested relationships themselves, so that
if a sample object links to a processor and the processor links to the
sample, the JSON won't recur infinitely. For any relationships, these
serializers will use PrimaryKeyRelatedFields.

The one exception is the ProjectSerializer because it will always include its summaries.
"""

from rest_framework import serializers

from scpca_portal.models import ComputedFile, Processor, Project, ProjectSummary, Sample


class ComputedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputedFile
        fields = (
            "processor",
            "project",
            "sample",
            "id",
            "type",
            "s3_bucket",
            "s3_key",
            "created_at",
            "updated_at",
        )

    processor = serializers.PrimaryKeyRelatedField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)


class ProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processor
        fields = (
            "computed_files",
            "samples",
            "id",
            "name",
            "version",
            "workflow_name",
            "created_at",
            "updated_at",
        )

    computed_files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    samples = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class ProjectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSummary
        fields = (
            "diagnosis",
            "seq_unit",
            "technology",
            "sample_count",
            "updated_at",
        )


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "computed_files",
            "samples",
            "summaries",
            "id",
            "pi_name",
            "project_title",
            "abstract",
            "project_contact",
            "disease_timings",
            "diagnoses",
            "seq_units",
            "technologies",
            "sample_count",
            "created_at",
            "updated_at",
        )

    # This breaks the general pattern of not using sub-serializers,
    # but we want these to always be included.
    summaries = ProjectSummarySerializer(many=True, read_only=True)

    computed_files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    samples = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            "computed_files",
            "project",
            "processors",
            "id",
            "has_cite_seq_data",
            "scpca_sample_id",
            "technology",
            "diagnosis",
            "subdiagnosis",
            "age_at_diagnosis",
            "sex",
            "disease_timing",
            "has_spinal_leptomeningeal_mets",
            "tissue_location",
            "braf_status",
            "treatment",
            "seq_unit",
            "created_at",
            "updated_at",
        )

    computed_files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    processors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
