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
        fields = [
            "created_at",
            "id",
            "project",
            "sample",
            "s3_bucket",
            "s3_key",
            "size_in_bytes",
            "type",
            "updated_at",
            "workflow_version",
        ]

    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")
    sample = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")


class ProjectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSummary
        fields = (
            "diagnosis",
            "sample_count",
            "seq_unit",
            "technology",
            "updated_at",
        )


class ProjectLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "abstract",
            "additional_metadata_keys",
            "computed_files",
            "contact_email",
            "contact_name",
            "created_at",
            "diagnoses_counts",
            "diagnoses",
            "disease_timings",
            "downloadable_sample_count",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_spatial_data",
            "human_readable_pi_name",
            "modalities",
            "pi_name",
            "sample_count",
            "samples",
            "scpca_id",
            "seq_units",
            "summaries",
            "technologies",
            "title",
            "updated_at",
        )

    # This breaks the general pattern of not using sub-serializers,
    # but we want these to always be included.
    summaries = ProjectSummarySerializer(many=True, read_only=True)
    computed_files = ComputedFileSerializer(read_only=True, many=True)
    samples = serializers.SlugRelatedField(many=True, read_only=True, slug_field="scpca_id")


class ProjectSerializer(ProjectLeafSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)


class SampleLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            "additional_metadata",
            "age_at_diagnosis",
            "cell_count",
            "computed_files",
            "created_at",
            "diagnosis",
            "disease_timing",
            "has_cite_seq_data",
            "has_bulk_rna_seq",
            "has_spatial_data",
            "modalities",
            "project",
            "scpca_id",
            "seq_units",
            "sex",
            "subdiagnosis",
            "technologies",
            "tissue_location",
            "treatment",
            "updated_at",
        )

    computed_files = ComputedFileSerializer(read_only=True, many=True)
    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")


class SampleSerializer(SampleLeafSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)
