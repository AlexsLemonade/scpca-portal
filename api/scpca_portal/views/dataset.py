from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetSerializer


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Dataset.objects.filter(is_ccdl=True).order_by("-created_at")
    ordering_fields = "__all__"
    serializer_class = DatasetSerializer

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

    def update(self, request, pk=None):
        return Response(
            {"detail": "Updates to datasets are not allowed at this time."},
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
