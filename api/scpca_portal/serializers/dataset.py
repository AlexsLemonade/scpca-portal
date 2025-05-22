from rest_framework import serializers

from scpca_portal.models import Dataset
from scpca_portal.serializers.computed_file import ComputedFileSerializer


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            "id",
            "data",
            "email",
            "start",
            "format",
            "stats",
            "data_hash",
            "metadata_hash",
            "readme_hash",
            "is_ccdl",
            "ccdl_name",
            "ccdl_project_id",
            "started_at",
            "is_started",
            "is_processing",
            "succeeded_at",
            "is_succeeded",
            "failed_at",
            "is_failed",
            "failed_reason",
            "expires_at",
            "is_expired",
            "terminated_at",
            "is_terminated",
            "terminated_reason",
            "computed_file",
        )
        read_only_fields = (
            "id",
            "data",
            "email",
            "start",
            "format",
            "stats",
            "data_hash",
            "metadata_hash",
            "readme_hash",
            "is_ccdl",
            "ccdl_name",
            "ccdl_project_id",
            "started_at",
            "is_started",
            "is_processing",
            "succeeded_at",
            "is_succeeded",
            "failed_at",
            "is_failed",
            "failed_reason",
            "expires_at",
            "is_expired",
            "terminated_at",
            "is_terminated",
            "terminated_reason",
            "computed_file",
        )


class DatasetDetailSerializer(DatasetSerializer):
    computed_file = ComputedFileSerializer(read_only=True, many=False)


class DatasetCreateSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta):
        modifiable_fields = ("format", "data", "email", "start")
        read_only_fields = tuple(
            set(DatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )


class DatasetUpdateSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta):
        modifiable_fields = ("data", "email", "start")
        read_only_fields = tuple(
            set(DatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )
