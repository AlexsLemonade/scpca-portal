from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Project
from scpca_portal.serializers import ProjectSerializer, SampleSerializer


class ProjectDetailSerializer(ProjectSerializer):
    samples = SampleSerializer(many=True, read_only=True)


class ProjectViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    lookup_field = "scpca_id"

    filterset_fields = {
        "scpca_id": ["exact"],
        "pi_name": ["exact"],
        "human_readable_pi_name": ["contains"],
        "has_bulk_rna_seq": ["exact"],
        "has_cite_seq_data": ["exact"],
        "has_spatial_data": ["exact"],
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
