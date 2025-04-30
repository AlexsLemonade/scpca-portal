from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetSerializer, DatasetUpdateSerializer


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    ordering_fields = "__all__"

    def get_serializer_class(self):
        if self.action == "update":
            return DatasetUpdateSerializer
        return DatasetSerializer

    def get_queryset(self):
        datasets = Dataset.objects.all()
        if self.action == "update":
            # only custom datasets can be updated
            datasets = datasets.filter(is_ccdl=False)
        elif self.action == "list":
            # only ccdl datasets should be publicallay listable
            datasets = datasets.filter(is_ccdl=True)
        else:
            datasets = datasets.none()  # prevent accidental exposure

        return datasets.order_by("-created_at")

    def create(self, request):
        return Response(
            {"detail": "Creating datasets is not allowed at this time."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def retrieve(self, request, pk=None):
        return Response(
            {"detail": "Retrieving individual datasets is not allowed at this time."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

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
