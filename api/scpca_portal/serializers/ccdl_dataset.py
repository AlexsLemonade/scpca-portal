from rest_framework import serializers

from scpca_portal.models import Dataset
from scpca_portal.serializers.computed_file import ComputedFileSerializer


class CCDLDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            "id",
            "data",
            "email",
            "start",
            "format",
            "regenerated_from",
            "includes_files_bulk",
            "includes_files_cite_seq",
            "includes_files_merged",
            "includes_files_multiplexed",
            "is_ccdl",
            "ccdl_name",
            "ccdl_project_id",
            "ccdl_modality",
            "data_hash",
            "metadata_hash",
            "readme_hash",
            "combined_hash",
            # TODO: Uncomment re-computed current hashes if hashing can be optimized for large
            # datasets (specifically portal wide) to avert a timeout upon list request.
            # "current_data_hash",
            # "current_metadata_hash",
            # "current_readme_hash",
            # "current_combined_hash",
            # "is_hash_changed",
            "estimated_size_in_bytes",
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

    computed_file = ComputedFileSerializer(read_only=True, many=False)

    current_combined_hash = serializers.SerializerMethodField(read_only=True, default=None)

    def get_current_combined_hash(self, obj):
        return Dataset.get_current_combined_hash(
            obj.current_data_hash, obj.current_metadata_hash, obj.current_readme_hash
        )


class CCDLDatasetDetailSerializer(CCDLDatasetSerializer):
    class Meta(CCDLDatasetSerializer.Meta):
        fields = (*CCDLDatasetSerializer.Meta.fields, "download_filename", "download_url")
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "context" in kwargs:
            # Only include the field `download_url` if a valid token is specified.
            # The token lookup happens in the view.
            if "token" not in kwargs["context"]:
                self.fields.pop("download_filename")
                self.fields.pop("download_url")
