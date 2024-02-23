from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import APIToken, ComputedFile
from scpca_portal.serializers import ComputedFileSerializer, ProjectLeafSerializer, SampleSerializer


class ComputedFileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputedFile
        fields = (
            "created_at",
            "download_url",
            "format",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "id",
            "modality",
            "project",
            "s3_bucket",
            "s3_key",
            "sample",
            "size_in_bytes",
            "updated_at",
            "workflow_version",
        )
        extra_kwargs = {
            "download_url": {
                "help_text": (
                    "This will contain an url to download the file. "
                    "You must send a valid [token](#tag/token) in order to receive this."
                )
            }
        }

    project = ProjectLeafSerializer(read_only=True)
    sample = SampleSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        super(ComputedFileDetailSerializer, self).__init__(*args, **kwargs)
        if "context" in kwargs:
            # Only include the field `download_url` if a valid token is
            # specified. The token lookup happens in the view.
            if "token" not in kwargs["context"]:
                self.fields.pop("download_url")


class ComputedFileViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ComputedFile.objects.order_by("-created_at")
    ordering_fields = "__all__"
    filterset_fields = ("project__id", "sample__id", "id")

    def get_serializer_class(self):
        if self.action == "list":
            return ComputedFileSerializer

        return ComputedFileDetailSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.

        This is looking for the API-KEY HTTP Header.
        """
        serializer_context = super(ComputedFileViewSet, self).get_serializer_context()

        token_id = self.request.META.get("HTTP_API_KEY")

        if token_id:
            token = APIToken.verify(token_id)
            if not token:
                raise PermissionDenied(
                    {"message": "Your token is not valid or not activated.", "token_id": token_id}
                )

            serializer_context.update({"token": token})

        return serializer_context
