from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema, extend_schema_view

from scpca_portal.models import APIToken, CCDLDataset
from scpca_portal.serializers import CCDLDatasetDetailSerializer, CCDLDatasetSerializer


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
    queryset = CCDLDataset.objects.order_by("ccdl_project_id")
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
            return CCDLDatasetSerializer

        return CCDLDatasetDetailSerializer

    def get_serializer_context(self):
        """
        Additional context is added to provide the serializer classes with the API token.
        """
        serializer_context = super(CCDLDatasetViewSet, self).get_serializer_context()

        if token_id := self.request.META.get("HTTP_API_KEY"):
            token = APIToken.verify(token_id)
            if not token:
                message = f"Token header value {token_id} is either invalid or inactive."
                raise PermissionDenied({"message": message, "token_id": token_id})

            serializer_context.update({"token": token})

        return serializer_context
