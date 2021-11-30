"""This file houses serializers which can be used for nested relationships.

These serializers do not use nested relationships themselves, so that
if a sample object links to a computed file and the computed file
links to the sample, the JSON won't recur infinitely. For any
relationships, these serializers will use PrimaryKeyRelatedFields or
SlugRelatedFields.

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

    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")
    sample = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")


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


class ProjectLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "scpca_id",
            "computed_file",
            "samples",
            "summaries",
            "pi_name",
            "human_readable_pi_name",
            "additional_metadata_keys",
            "title",
            "abstract",
            "contact_name",
            "contact_email",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_spatial_data",
            "modalities",
            "disease_timings",
            "diagnoses",
            "diagnoses_counts",
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
    samples = serializers.SlugRelatedField(many=True, read_only=True, slug_field="scpca_id")


class ProjectSerializer(ProjectLeafSerializer):
    computed_file = ComputedFileSerializer(read_only=True)


class SampleLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            "scpca_id",
            "computed_file",
            "project",
            "has_cite_seq_data",
            "technologies",
            "diagnosis",
            "subdiagnosis",
            "age_at_diagnosis",
            "sex",
            "disease_timing",
            "tissue_location",
            "seq_units",
            "cell_count",
            "additional_metadata",
            "created_at",
            "updated_at",
        )

    computed_file = serializers.PrimaryKeyRelatedField(read_only=True)
    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")


class SampleSerializer(SampleLeafSerializer):
    computed_file = ComputedFileSerializer(read_only=True)
