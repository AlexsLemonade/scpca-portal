from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset
from scpca_portal.serializers import (
    DatasetCreateSerializer,
    DatasetDetailSerializer,
    DatasetSerializer,
    DatasetUpdateSerializer,
)


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    ordering_fields = "__all__"

    def get_serializer_class(self):
        match self.action:
            case "create":
                return DatasetCreateSerializer
            case "list":
                return DatasetSerializer
            case "retrieve":
                return DatasetDetailSerializer
            case "update":
                return DatasetUpdateSerializer

    def get_queryset(self):
        datasets = Dataset.objects.all()
        if self.action in ["create", "update"]:
            # only custom datasets can be updated
            datasets = datasets.filter(is_ccdl=False)
        elif self.action == "list":
            # only ccdl datasets should be publicly listable
            datasets = datasets.filter(is_ccdl=True)

        return datasets.order_by("-created_at")

    # Partial update and delete are intentionally disabled
    def partial_update(self, request, pk=None):
        return Response(
            {"detail": "Partial updates to datasets are not allowed at this time."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, pk=None):
        return Response(
            {"detail": "Deleting datasets is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
