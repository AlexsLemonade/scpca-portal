from rest_framework import serializers

from pydantic import ValidationError as PydanticValidationError

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


class DatasetDetailSerializer(DatasetSerializer):
    computed_file = ComputedFileSerializer(read_only=True, many=False)


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
        modifiable_fields = ("data", "email", "start")
        read_only_fields = tuple(
            set(DatasetSerializer.Meta.read_only_fields) - set(modifiable_fields)
        )

    def validate_data(self, value):
        try:
            return Dataset.validate_data(value, self.instance.format)
        # serializer exceptions return a 400 response to the client
        except PydanticValidationError as e:
            raise serializers.ValidationError({"detail": f"Invalid data structure: {e}"})
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Data validation failed: {e}"})
