from rest_framework import serializers

from scpca_portal.models import ComputedFile


class ComputedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputedFile
        fields = (
            "created_at",
            "format",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "id",
            "includes_merged",
            "metadata_only",
            "portal_metadata_only",
            "modality",
            "project",
            "s3_bucket",
            "s3_key",
            "sample",
            "size_in_bytes",
            "updated_at",
            "workflow_version",
        )

    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")
    sample = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")
