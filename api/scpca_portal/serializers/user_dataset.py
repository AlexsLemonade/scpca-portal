from rest_framework import serializers

from pydantic import ValidationError as PydanticValidationError

from scpca_portal.models import UserDataset
from scpca_portal.serializers.computed_file import ComputedFileSerializer


class UserDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDataset
        fields = (
            "id",
            "format",
            "data",
            "email",
            "start",
            "regenerated_from",
            "includes_files_bulk",
            "includes_files_cite_seq",
            "includes_files_merged",
            "includes_files_multiplexed",
            "estimated_size_in_bytes",
            "data_hash",
            "metadata_hash",
            "readme_hash",
            "combined_hash",
            "current_data_hash",
            "current_metadata_hash",
            "current_readme_hash",
            "current_combined_hash",
            "is_hash_changed",
            "total_sample_count",
            "diagnoses_summary",
            "files_summary",
            "project_diagnoses",
            "project_modality_counts",
            "modality_count_mismatch_projects",
            "project_sample_counts",
            "project_titles",
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
        return UserDataset.get_current_combined_hash(
            obj.current_data_hash, obj.current_metadata_hash, obj.current_readme_hash
        )


class UserDatasetDetailSerializer(UserDatasetSerializer):
    class Meta(UserDatasetSerializer.Meta):
        fields = (*UserDatasetSerializer.Meta.fields, "download_filename", "download_url")
        extra_kwargs = {
            "download_filename": {
                "help_text": (
                    "This will contain the download file's name. "
                    "You must send a valid [token](#tag/token) in order to receive this."
                )
            },
            "download_url": {
                "help_text": (
                    "This will contain a url to download the file. "
                    "You must send a valid [token](#tag/token) "
                    "for this attribute to be present in the response."
                )
            },
        }

    computed_file = ComputedFileSerializer(read_only=True, many=False)

    def __init__(self, *args, **kwargs):
        super(UserDatasetDetailSerializer, self).__init__(*args, **kwargs)
        if "context" in kwargs:
            # Only include the field `download_url` if a valid token is
            # specified. The token lookup happens in the view.
            if "token" not in kwargs["context"]:
                self.fields.pop("download_filename")
                self.fields.pop("download_url")


class UserDatasetCreateSerializer(UserDatasetSerializer):
    class Meta(UserDatasetSerializer.Meta):
        modifiable_fields = ("format", "data", "email", "start")
        read_only_fields = tuple(
            set(UserDatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        if "data" in validated_attrs:
            try:
                validated_attrs["data"] = UserDataset.validate_data(
                    validated_attrs["data"], validated_attrs["format"]
                )

            # serializer exceptions return a 400 response to the client
            except PydanticValidationError as e:
                raise serializers.ValidationError({"detail": f"Invalid data structure: {e}"})
            except Exception as e:
                raise serializers.ValidationError({"detail": f"Data validation failed: {e}"})

        return validated_attrs


class UserDatasetUpdateSerializer(UserDatasetSerializer):
    class Meta(UserDatasetSerializer.Meta):
        modifiable_fields = ("format", "data", "email", "start")
        read_only_fields = tuple(
            set(UserDatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )
        extra_kwargs = {"format": {"required": False}}

    def validate_data(self, value):
        # Either the incoming or original format
        new_format = self.initial_data.get("format", self.instance.format)
        try:
            return UserDataset.validate_data(value, new_format)
        # serializer exceptions return a 400 response to the client
        except PydanticValidationError as e:
            raise serializers.ValidationError({"detail": f"Invalid data structure: {e}"})
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Data validation failed: {e}"})
