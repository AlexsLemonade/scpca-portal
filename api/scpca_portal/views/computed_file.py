from rest_framework import serializers, viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import ComputedFile
from scpca_portal.serializers import ComputedFileSerializer, ProjectSerializer, SampleSerializer


class ComputedFileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputedFile
        fields = (
            "project",
            "sample",
            "id",
            "type",
            "s3_bucket",
            "s3_key",
            "download_url",
            "created_at",
            "updated_at",
        )

    project = ProjectSerializer(read_only=True)
    sample = SampleSerializer(read_only=True)


class ComputedFileViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ComputedFile.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    filterset_fields = (
        "project__id",
        "sample__id",
        "id",
        "type",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ComputedFileSerializer

        return ComputedFileDetailSerializer
