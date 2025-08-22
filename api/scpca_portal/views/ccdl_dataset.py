from rest_framework import viewsets

from drf_spectacular.utils import extend_schema, extend_schema_view

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetDetailSerializer, DatasetSerializer


@extend_schema_view(
    list=extend_schema(
        auth=False,
        description="""CCDL Datasets are immutable pre-generated datasets managed by
            the Data Lab. CCDL Datasets look similar to Datasets except that they
            have a couple additional properties that describe their contents.""",
    ),
    retrieve=extend_schema(
        description="""CCDL Datasets are immutable pre-generated datasets.
        In order to retrieve a CCDL dataset with a download_url you must
        pass a API-KEY header.
        """
    ),
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
