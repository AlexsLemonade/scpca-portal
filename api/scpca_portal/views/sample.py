from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Sample
from scpca_portal.serializers import (
    ComputedFileSerializer,
    ProcessorSerializer,
    ProjectSerializer,
    SampleSerializer,
)


class SampleDetailSerializer(SampleSerializer):
    computed_files = ComputedFileSerializer(many=True, read_only=True)
    processors = ProcessorSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)


class SampleViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Sample.objects.all().order_by("-created_at")
    ordering_fields = "__all__"
    filterset_fields = (
        "project__id",
        "id",
        "has_cite_seq_data",
        "scpca_sample_id",
        "technology",
        "diagnosis",
        "subdiagnosis",
        "age_at_diagnosis",
        "sex",
        "disease_timing",
        "has_spinal_leptomeningeal_mets",
        "tissue_location",
        "braf_status",
        "treatment",
        "seq_unit",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return SampleSerializer

        return SampleDetailSerializer
