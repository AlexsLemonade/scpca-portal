from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Sample
from scpca_portal.serializers import ComputedFileSerializer, ProjectSerializer, SampleSerializer


class SampleDetailSerializer(SampleSerializer):
    computed_file = ComputedFileSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)


class SampleViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Sample.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    lookup_field = "scpca_sample_id"
    filterset_fields = (
        "project__id",
        "id",
        "has_cite_seq_data",
        "scpca_sample_id",
        "technologies",
        "diagnosis",
        "subdiagnosis",
        "age_at_diagnosis",
        "sex",
        "disease_timing",
        "tissue_location",
        "treatment",
        "seq_units",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return SampleSerializer

        return SampleDetailSerializer
