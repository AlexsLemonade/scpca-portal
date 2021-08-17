from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import ComputedFile
from scpca_portal.serializers import ComputedFileSerializer, ProcessorSerializer, ProjectSerializer


class ComputedFileDetailSerializer(ComputedFileSerializer):
    processor = ProcessorSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)


class ComputedFileViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ComputedFile.objects.all().order_by("-created_at")
    filterset_fields = (
        "processor__id",
        "project__id",
        "sample__id",
        "id",
        "type",
        "s3_bucket",
        "s3_key",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ComputedFileSerializer

        return ComputedFileDetailSerializer
