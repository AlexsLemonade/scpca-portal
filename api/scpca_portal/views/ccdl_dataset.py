from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetDetailSerializer, DatasetSerializer


class CCDLDatasetViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.all(is_ccdl=True).order_by("scpca_id")
    ordering_fields = "__all__"
    filterset_fields = (
        "id",
        "is_ccdl",
        "ccdl_name",
        "ccdl_project_id",
        "format",
        # data  # TODO: consider if we want to query for modality on CCDL datasets
        # or included project ids, modalities, and bulk in custom datasets
    )

    def get_serializer_class(self):
        if self.action == "list":
            return DatasetSerializer

        return DatasetDetailSerializer
