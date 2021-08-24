from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Project
from scpca_portal.serializers import ComputedFileSerializer, ProjectSerializer, SampleSerializer


class ProjectDetailSerializer(ProjectSerializer):
    computed_file = ComputedFileSerializer(read_only=True)
    samples = SampleSerializer(many=True, read_only=True)


class ProjectViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    filterset_fields = {
        "id": ["exact"],
        "pi_name": ["exact"],
        "title": ["contains"],
        "abstract": ["contains"],
        "technologies": ["exact", "contains"],
        "diagnoses": ["exact", "contains"],
        "seq_units": ["exact", "contains"],
        "disease_timings": ["exact", "contains"],
    }

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectSerializer

        return ProjectDetailSerializer
