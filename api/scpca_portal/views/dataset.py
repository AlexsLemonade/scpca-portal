from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset
from scpca_portal.serializers import DatasetSerializer


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Dataset.objects.order_by("-created_at")
    ordering_fields = "__all__"

    def get_serializer_class(self):
        # TODO: uncomment below (only return DatasetSerializer during list action)
        # if self.action == "list":
        return DatasetSerializer
