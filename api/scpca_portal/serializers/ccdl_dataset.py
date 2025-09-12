from collections import OrderedDict

from rest_framework import serializers

from scpca_portal.models import Dataset


class CCDLDatasetSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    # it's necessary to rename data attr because serializer.Serializer needs it own data attr.
    # this attr is renamed to data on output in to_representation method
    _data = serializers.JSONField(source="data", read_only=True)
    email = serializers.EmailField(read_only=True, allow_null=True)
    start = serializers.BooleanField(read_only=True)

    format = serializers.CharField(read_only=True)
    regenerated_from = serializers.UUIDField(read_only=True, allow_null=True)

    data_hash = serializers.CharField(read_only=True, allow_null=True)
    metadata_hash = serializers.CharField(read_only=True, allow_null=True)
    readme_hash = serializers.CharField(read_only=True, allow_null=True)
    combined_hash = serializers.CharField(read_only=True, allow_null=True)
    current_data_hash = serializers.ReadOnlyField()
    current_metadata_hash = serializers.ReadOnlyField()
    current_readme_hash = serializers.ReadOnlyField()
    current_combined_hash = serializers.SerializerMethodField(read_only=True)
    is_hash_changed = serializers.ReadOnlyField()

    includes_files_bulk = serializers.BooleanField(read_only=True)
    includes_files_cite_seq = serializers.BooleanField(read_only=True)
    includes_files_merged = serializers.BooleanField(read_only=True)
    includes_files_multiplexed = serializers.BooleanField(read_only=True)

    is_ccdl = serializers.BooleanField(read_only=True)
    ccdl_name = serializers.CharField(read_only=True, allow_null=True)
    ccdl_project_id = serializers.CharField(read_only=True, allow_null=True)
    ccdl_modality = serializers.CharField(read_only=True, allow_null=True)

    started_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_started = serializers.BooleanField(read_only=True)
    pending_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_pending = serializers.BooleanField(read_only=True)
    processing_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_processing = serializers.BooleanField(read_only=True)
    succeeded_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_succeeded = serializers.BooleanField(read_only=True)
    failed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_failed = serializers.BooleanField(read_only=True)
    failed_reason = serializers.CharField(read_only=True, allow_null=True)
    expires_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_expired = serializers.BooleanField(read_only=True)
    terminated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_terminated = serializers.BooleanField(read_only=True)
    terminated_reason = serializers.CharField(read_only=True, allow_null=True)

    computed_file = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_current_combined_hash(self, obj):
        return Dataset.get_current_combined_hash(
            obj.current_data_hash, obj.current_metadata_hash, obj.current_readme_hash
        )

    # rename the _data attr to data for output json
    def to_representation(self, instance):
        instance_rep = super().to_representation(instance)
        corrected_instance_rep = {
            (k if k != "_data" else "data"): v for k, v in instance_rep.items()
        }
        return OrderedDict(corrected_instance_rep)
