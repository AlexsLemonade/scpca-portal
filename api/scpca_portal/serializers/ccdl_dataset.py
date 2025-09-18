from collections import OrderedDict

from rest_framework import serializers

from scpca_portal.models import Dataset
from scpca_portal.serializers.computed_file import ComputedFileSerializer


class CCDLDatasetSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    # It's necessary to rename the data attr as serializer.Serializer needs its own data attr.
    # The "_data" attr is renamed to "data" for output purposes in to_representation below.
    _data = serializers.JSONField(source="data", read_only=True)
    email = serializers.EmailField(read_only=True, allow_null=True)
    start = serializers.BooleanField(read_only=True)
    format = serializers.CharField(read_only=True)
    regenerated_from = serializers.UUIDField(read_only=True, allow_null=True)

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

    computed_file = ComputedFileSerializer(read_only=True, many=False)

    # Rename the "_data attr" to "data" for output json
    def to_representation(self, instance):
        instance_rep = super().to_representation(instance)
        corrected_instance_rep = {
            (k if k != "_data" else "data"): v for k, v in instance_rep.items()
        }
        return OrderedDict(corrected_instance_rep)


class CCDLDatasetDetailSerializer(CCDLDatasetSerializer):
    download_filename = serializers.SerializerMethodField(read_only=True)
    download_url = serializers.SerializerMethodField(read_only=True)

    def get_download_filename(self, obj):
        dataset = Dataset.objects.filter(pk=obj.pk).first()
        return dataset.download_filename

    def get_download_url(self, obj):
        dataset = Dataset.objects.filter(pk=obj.pk).first()
        return dataset.download_url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "context" in kwargs:
            # Only include the field `download_url` if a valid token is specified.
            # The token lookup happens in the view.
            if "token" not in kwargs["context"]:
                self.fields.pop("download_filename")
                self.fields.pop("download_url")
