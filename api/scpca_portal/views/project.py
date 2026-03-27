from rest_framework import viewsets

from drf_spectacular.utils import extend_schema
from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal import filter
from scpca_portal.models import Project
from scpca_portal.serializers import ProjectDetailSerializer, ProjectSerializer

ProjectFilterSet = filter.build_auto_filterset(
    Project,
    auto_fields=[
        "scpca_id",
        "pi_name",
        "has_bulk_rna_seq",
        "has_cite_seq_data",
        "has_multiplexed_data",
        "has_single_cell_data",
        "has_spatial_data",
        "includes_anndata",
        "includes_cell_lines",
        "includes_merged_anndata",
        "includes_merged_sce",
        "includes_xenografts",
        "diagnoses",
        "seq_units",
        "modalities",
        "organisms",
        "technologies",
        "disease_timings",
        "human_readable_pi_name",
        "title",
        "abstract",
        # counts
        "sample_count",
        "downloadable_sample_count",
        "multiplexed_sample_count",
        "unavailable_samples_count",
        # timestamps
        "created_at",
        "updated_at",
    ],
)


@extend_schema(auth=False)
class ProjectViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().order_by("created_at")
    ordering_fields = "__all__"
    lookup_field = "scpca_id"
    filterset_class = ProjectFilterSet

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectSerializer

        return ProjectDetailSerializer
