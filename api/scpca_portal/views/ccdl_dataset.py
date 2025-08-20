from rest_framework import viewsets

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetDetailSerializer, DatasetSerializer


class CCDLDatasetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.filter(is_ccdl=True).order_by("ccdl_project_id")
    ordering_fields = "__all__"
    filterset_fields = {
        "id": ["exact"],
        "ccdl_name": ["exact"],
        "ccdl_project_id": ["exact", "isnull"],
        "ccdl_modality": ["exact"],
        "format": ["exact"],
    }

    def get_serializer_class(self):
        if self.action == "list":
            return DatasetSerializer

        return DatasetDetailSerializer
