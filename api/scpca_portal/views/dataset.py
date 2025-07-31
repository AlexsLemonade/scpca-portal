from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.exceptions import DatasetError, JobError
from scpca_portal.models import APIToken, Dataset, Job
from scpca_portal.serializers import (
    DatasetCreateSerializer,
    DatasetDetailSerializer,
    DatasetUpdateSerializer,
)

logger = get_and_configure_logger(__name__)


class DatasetViewSet(viewsets.ModelViewSet):
    ordering_fields = "__all__"

    def get_queryset(self):
        return Dataset.objects.filter(is_ccdl=False)

    def get_object(self):
        self.validate_token(self.request)

        queryset = self.get_queryset()
        dataset = get_object_or_404(queryset, pk=self.kwargs[self.lookup_field])

        return dataset

    def validate_token(self, request):
        token_id = request.META.get("HTTP_API_KEY")
        token = APIToken.verify(token_id) if token_id else None
        if not token:
            raise PermissionDenied(
                {
                    "message": (
                        "A token was either not passed or is invalid. "
                        "A valid token must be present to "
                        "retrieve, create or modify custom datasets."
                    ),
                    "token_id": token_id,
                }
            )

    def retrieve(self, request, pk=None):
        dataset = self.get_object()
        serializer = DatasetDetailSerializer(dataset, many=False)
        return Response(serializer.data)

    def create(self, request):
        self.validate_token(request)

        serializer = DatasetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        dataset = serializer.save()

        if dataset.start:
            dataset_job = Job.get_dataset_job(dataset)
            try:
                dataset_job.submit()
            except (DatasetError, JobError):
                logger.info(f"{dataset} job (attempt {dataset_job.attempt}) is being requeued.")
                dataset_job.increment_attempt_or_fail()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        existing_dataset = self.get_object()
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
            try:
                dataset_job.submit()
            except (DatasetError, JobError):
                logger.info(
                    f"{modified_dataset} job (attempt {dataset_job.attempt}) is being requeued."
                )
                dataset_job.increment_attempt_or_fail()

        return Response(serializer.data)

    # List action is disabled
    def list(self, request):
        return Response(
            {"detail": "Listing of custom datasets is unavailable."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Partial update action is disabled
    def partial_update(self, request, pk=None):
        return Response(
            {"detail": "Partial updates to datasets are not allowed at this time."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Delete action is disabled
    def destroy(self, request, pk=None):
        return Response(
            {"detail": "Deleting datasets is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
