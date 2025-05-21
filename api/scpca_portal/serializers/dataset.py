from rest_framework import serializers

from scpca_portal.models import Dataset

from .computed_file import ComputedFileSerializer


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


class DatasetDetailSerializer(DatasetSerializer):
    computed_file = ComputedFileSerializer(read_only=True, many=False)


class DatasetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            "data",
            "email",
            "format",
            "start",
            "id",
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


class DatasetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            "data",
            "email",
            "start",
            "id",
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
