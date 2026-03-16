from rest_framework import viewsets

from drf_spectacular.utils import extend_schema
from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal import filter
from scpca_portal.models import Sample
from scpca_portal.serializers import ComputedFileSerializer, ProjectSerializer, SampleSerializer


class SampleDetailSerializer(SampleSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)
    project = ProjectSerializer(read_only=True)


SampleFilterSet = filter.build_auto_filterset(
    Sample,
    auto_fields=[
        "scpca_id",
        "has_cite_seq_data",
        "has_bulk_rna_seq",
        "has_multiplexed_data",
        "has_single_cell_data",
        "has_spatial_data",
        "includes_anndata",
        "is_cell_line",
        "is_xenograft",
        "technologies",
        "diagnosis",
        "subdiagnosis",
        "age",
        "age_timing",
        "sex",
        "disease_timing",
        "tissue_location",
        "treatment",
        "seq_units",
        # counts
        "demux_cell_count_estimate_sum",
        "sample_cell_count_estimate",
        # timestamps
        "created_at",
        "updated_at",
    ],
    extra_fields={
        "project__scpca_id": ["exact"],
    },
)


@extend_schema(auth=False)
class SampleViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Sample.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    lookup_field = "scpca_id"
    filterset_class = SampleFilterSet

    def get_serializer_class(self):
        if self.action == "list":
            return SampleSerializer

        return SampleDetailSerializer
