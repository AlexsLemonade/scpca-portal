"""This file houses serializers which can be used for nested relationships.

These serializers do not use nested relationships themselves, so that
if a sample object links to a computed file and the computed file
links to the sample, the JSON won't recur infinitely. For any
relationships, these serializers will use PrimaryKeyRelatedFields.

The one exception is the ProjectSerializer because it will always include its summaries.
"""

from rest_framework import serializers

from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample


class ComputedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputedFile
        fields = (
            "project",
            "sample",
            "id",
            "type",
            "s3_bucket",
            "s3_key",
            "size_in_bytes",
            "created_at",
            "updated_at",
        )

    project = serializers.PrimaryKeyRelatedField(read_only=True)
    sample = serializers.PrimaryKeyRelatedField(read_only=True)


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
            "computed_file",
            "samples",
            "summaries",
            "id",
            "pi_name",
            "title",
            "abstract",
            "contact",
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

    computed_file = serializers.PrimaryKeyRelatedField(read_only=True)
    samples = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            "computed_file",
            "project",
            "id",
            "has_cite_seq_data",
            "scpca_sample_id",
            "technologies",
            "diagnosis",
            "subdiagnosis",
            "age_at_diagnosis",
            "sex",
            "disease_timing",
            "tissue_location",
            "treatment",
            "seq_units",
            "additional_metadata",
            "created_at",
            "updated_at",
        )

    computed_file = serializers.PrimaryKeyRelatedField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
