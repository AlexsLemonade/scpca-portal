from rest_framework import serializers

from scpca_portal.models import ProjectSummary


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
