from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import APIException

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.exceptions import DatasetError, JobError
from scpca_portal.models import Dataset, Job
from scpca_portal.serializers import (
    DatasetCreateSerializer,
    DatasetDetailSerializer,
    DatasetUpdateSerializer,
)

logger = get_and_configure_logger(__name__)


class UpdateProcessingDatasetError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Invalid request: Processing datasets cannot be modified."
    default_code = "conflict"


@extend_schema(
    examples=[
        OpenApiExample("Example Dataset Response"),
    ],
)
@extend_schema_view(
    create=extend_schema(
        description="""Datasets are described here.
        **Format is required at time of creation.**
        **An API-KEY header is required to set start to `true` at time of creation.**"""
    ),
    retrieve=extend_schema(
        description="Retrieve Dataset by ID. `API-KEY` header is required for `download_url` to be populated.",
    ),
    update=extend_schema(description="Update the Dataset data, email or start values."),
)
class DatasetViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    model = Dataset
    lookup_field = "id"

    def get_queryset(self):
        return Dataset.objects.filter(is_ccdl=False)

    def get_serializer_class(self):
        if self.action == "create":
            return DatasetCreateSerializer

        if self.action == "update":
            return DatasetUpdateSerializer

        return DatasetDetailSerializer

    def get_object(self):
        queryset = self.get_queryset()
        dataset = get_object_or_404(queryset, pk=self.kwargs[self.lookup_field])

        return dataset

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        dataset = serializer.save()

        if dataset.start:
            dataset_job = Job.get_dataset_job(dataset)
            try:
                dataset_job.submit()
            except (DatasetError, JobError):
                logger.info(f"{dataset} job (attempt {dataset_job.attempt}) is being requeued.")
                dataset_job.increment_attempt_or_fail()

    def perform_update(self, serializer):

        found_dataset = self.get_object()

        if found_dataset.start:
            raise UpdateProcessingDatasetError

        serializer.is_valid(raise_exception=True)

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
