from rest_framework import viewsets
from drf_spectacular.utils import extend_schema_view, extend_schema

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetDetailSerializer, DatasetSerializer


@extend_schema_view(
    list=extend_schema(
        auth=False,
        description="""CCDL Datasets are immutable pre-generated datasets managed by the Data Lab.
            ccdl_name describes the contents
            ccdl_project_id indicates if the dataset only contains samples limited to a specific project.
            ccdl_modality indicates if the dataset only contains samples limited to a specific modality.
            All other attributes are the same as user defined dataset."""
    ),
    retrieve=extend_schema(
        description="""CCDL Datasets are immutable pre-generated datasets.
        You can retrieve a download_url by passing an API-KEY header with an activated token's id as the value.
        """
    )
)
class CCDLDatasetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.filter(is_ccdl=True).order_by("ccdl_project_id")
    ordering_fields = "__all__"
    filterset_fields = (
        "id",
        "ccdl_name",
        "ccdl_project_id",
        "ccdl_modality",
        "format",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return DatasetSerializer

        return DatasetDetailSerializer
