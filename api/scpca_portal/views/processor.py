from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Processor
from scpca_portal.serializers import ComputedFileSerializer, ProcessorSerializer, SampleSerializer


class ProcessorDetailSerializer(ProcessorSerializer):
    computed_files = ComputedFileSerializer(many=True, read_only=True)
    samples = SampleSerializer(many=True, read_only=True)


class ProcessorViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Processor.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    filterset_fields = (
        "id",
        "name",
        "version",
        "workflow_name",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProcessorSerializer

        return ProcessorDetailSerializer
