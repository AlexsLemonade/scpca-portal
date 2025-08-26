from django.contrib.postgres.fields import ArrayField
from rest_framework import viewsets

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Sample
from scpca_portal.serializers import ComputedFileSerializer, ProjectSerializer, SampleSerializer


class SampleDetailSerializer(SampleSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)
    project = ProjectSerializer(read_only=True)


class SampleFilterSet(filters.FilterSet):
    """
    Custom FilterSet to support ArrayField.
    """

    class Meta:
        model = Sample
        fields = [
            "scpca_id",
            "project__scpca_id",
            "scpca_id",
            "has_cite_seq_data",
            "has_bulk_rna_seq",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
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
        ]

        filter_overrides = {
            ArrayField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            }
        }


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
