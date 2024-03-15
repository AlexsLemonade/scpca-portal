from rest_framework import viewsets

from django_filters import rest_framework as filters
from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Project
from scpca_portal.serializers import ProjectSerializer, SampleSerializer


class ProjectDetailSerializer(ProjectSerializer):
    samples = SampleSerializer(many=True, read_only=True)


class ProjectFilter(filters.FilterSet):
    diagnoses = filters.CharFilter(field_name="diagnoses", lookup_expr="icontains")
    seq_units = filters.CharFilter(field_name="seq_units", lookup_expr="icontains")
    modalities = filters.CharFilter(field_name="modalities", lookup_expr="icontains")
    organisms = filters.CharFilter(field_name="organisms", lookup_expr="icontains")
    technologies = filters.CharFilter(field_name="technologies", lookup_expr="icontains")
    disease_timings = filters.CharFilter(field_name="disease_timings", lookup_expr="icontains")
    human_readable_pi_name = filters.CharFilter(
        field_name="human_readable_pi_name", lookup_expr="icontains"
    )
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    abstract = filters.CharFilter(field_name="abstract", lookup_expr="icontains")

    class Meta:
        model = Project
        fields = [
            "scpca_id",
            "pi_name",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
            "includes_cell_lines",
            "includes_xenografts",
        ]


class ProjectViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().order_by("created_at")
    ordering_fields = "__all__"
    lookup_field = "scpca_id"
    filterset_class = ProjectFilter

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectSerializer

        return ProjectDetailSerializer
