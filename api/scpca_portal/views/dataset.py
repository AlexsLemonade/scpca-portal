from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.models import Dataset, Job
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
            case "update":
                return DatasetUpdateSerializer

    def get_queryset(self):
        datasets = Dataset.objects.all()
        if self.action in ["update"]:
            # only custom datasets can be updated
            datasets = datasets.filter(is_ccdl=False)

        return datasets.order_by("-created_at")

    def list(self, request):
        queryset = Dataset.objects.filter(is_ccdl=True)
        serializer = DatasetSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = DatasetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        dataset = serializer.save()

        if dataset.start:
            dataset_job = Job.get_dataset_job(dataset)
            dataset_job.submit()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = Dataset.objects.filter()
        dataset = get_object_or_404(queryset, pk=pk)
        serializer = DatasetDetailSerializer(dataset, many=False)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = Dataset.objects.filter(is_ccdl=False)
        existing_dataset = get_object_or_404(queryset, pk=pk)
        if existing_dataset.start:
            return Response(
                {"detail": "Invalid request: Processing dataset cannot be modified."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = DatasetUpdateSerializer(existing_dataset, data=request.data)
        serializer.is_valid(raise_exception=False)
        modified_dataset = serializer.save()

        if modified_dataset.start:
            dataset_job = Job.get_dataset_job(modified_dataset)
            dataset_job.submit()

        return Response(serializer.data)

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

    def perform_update(self, serializer):
        dataset = serializer.save()
        if dataset.start:
            # If dataset already has active job, don't allow user to spawn additional job
            if dataset.is_started or dataset.is_processing:
                return

            self.submit_job(dataset)

    def submit_job(self, dataset: Dataset):
        """Create and submit a user generated dataset job."""
        dataset_job = Job.get_dataset_job(dataset)
        dataset_job.submit()

        # Reset start attribute so dataset can be regenerated
        dataset.start = False
        dataset.save()
