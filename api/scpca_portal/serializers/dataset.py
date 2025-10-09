from rest_framework import serializers

from pydantic import ValidationError as PydanticValidationError

from scpca_portal.exceptions import DatasetFormatChangeError, UpdateProcessingDatasetError
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
            "data_hash",
            "metadata_hash",
            "readme_hash",
            "combined_hash",
            "current_data_hash",
            "current_metadata_hash",
            "current_readme_hash",
            "current_combined_hash",
            "is_hash_changed",
            "includes_files_bulk",
            "includes_files_cite_seq",
            "includes_files_merged",
            "estimated_size_in_bytes",
            "total_sample_count",
            "diagnoses_summary",
            "files_summary",
            "project_diagnoses",
            "project_modality_counts",
            "modality_count_mismatch_projects",
            "project_sample_counts",
            "project_titles",
            "is_ccdl",
            "ccdl_name",
            "ccdl_project_id",
            "ccdl_modality",
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
        read_only_fields = fields

    current_combined_hash = serializers.SerializerMethodField(read_only=True, default=None)

    def get_current_combined_hash(self, obj):
        return Dataset.get_current_combined_hash(
            obj.current_data_hash, obj.current_metadata_hash, obj.current_readme_hash
        )


class DatasetDetailSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta):
        fields = (*DatasetSerializer.Meta.fields, "download_url")
        extra_kwargs = {
            "download_url": {
                "help_text": (
                    "This will contain a url to download the file. "
                    "You must send a valid [token](#tag/token) "
                    "for this attribute to be present in the response."
                )
            }
        }

    computed_file = ComputedFileSerializer(read_only=True, many=False)

    def __init__(self, *args, **kwargs):
        super(DatasetDetailSerializer, self).__init__(*args, **kwargs)
        if "context" in kwargs:
            # Only include the field `download_url` if a valid token is
            # specified. The token lookup happens in the view.
            if "token" not in kwargs["context"]:
                self.fields.pop("download_url")


class DatasetCreateSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta):
        modifiable_fields = ("format", "data", "email", "start")
        read_only_fields = tuple(
            set(DatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        if "data" in validated_attrs:
            try:
                validated_attrs["data"] = Dataset.validate_data(
                    validated_attrs["data"], validated_attrs["format"]
                )

            # serializer exceptions return a 400 response to the client
            except PydanticValidationError as e:
                raise serializers.ValidationError({"detail": f"Invalid data structure: {e}"})
            except Exception as e:
                raise serializers.ValidationError({"detail": f"Data validation failed: {e}"})

        return validated_attrs


class DatasetUpdateSerializer(DatasetSerializer):
    class Meta(DatasetSerializer.Meta):
        modifiable_fields = ("format", "data", "email", "start")
        read_only_fields = tuple(
            set(DatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )
        extra_kwargs = {"format": {"required": False}}

    def validate_format(self, value):
        original_format = self.instance.format
        is_format_changed = value != original_format

        # No format change allowed for processing datasets and returns 409
        if self.instance.start and (value and is_format_changed):
            raise UpdateProcessingDatasetError

        if value is None or not is_format_changed:
            return original_format

        try:
            is_original_data_empty = not self.instance.data

            # Format change allowed only if data is empty
            if is_format_changed and not is_original_data_empty:
                raise DatasetFormatChangeError

            return value
        # serializer exceptions return a 400 response to the client
        except DatasetFormatChangeError as e:
            raise serializers.ValidationError({"detail": f"{e}"})

    def validate_data(self, value):
        try:
            return Dataset.validate_data(value, self.instance.format)
        # serializer exceptions return a 400 response to the client
        except PydanticValidationError as e:
            raise serializers.ValidationError({"detail": f"Invalid data structure: {e}"})
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Data validation failed: {e}"})
