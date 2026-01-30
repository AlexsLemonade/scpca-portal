from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.exceptions import (
    DatasetError,
    DatasetFormatChangeError,
    JobError,
    UpdateProcessingDatasetError,
)
from scpca_portal.models import APIToken, Job, UserDataset
from scpca_portal.serializers import (
    UserDatasetCreateSerializer,
    UserDatasetDetailSerializer,
    UserDatasetUpdateSerializer,
)

logger = get_and_configure_logger(__name__)


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
        description="""Retrieve Dataset by ID. Datasts are immutable pre-generated datasets.
        In order to retrieve a CCDL dataset with a download_url you must
        pass a API-KEY header.
        """
    ),
    update=extend_schema(description="Update the Dataset data, email or start values."),
)
class DatasetViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserDataset.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return UserDatasetCreateSerializer

        if self.action == "update":
            return UserDatasetUpdateSerializer

        return UserDatasetDetailSerializer

    def get_serializer_context(self):
        """
        Additional context is added to provide the serializer classes with the API token.
        """
        serializer_context = super().get_serializer_context()

        if token_id := self.request.META.get("HTTP_API_KEY"):
            token = APIToken.verify(token_id)
            if not token:
                message = f"Token header value {token_id} is either invalid or inactive."
                raise PermissionDenied({"message": message, "token_id": token_id})

            serializer_context.update({"token": token})

        return serializer_context

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

    def update(self, request, *args, **kwargs):
        found_dataset = self.get_object()

        if found_dataset.start:
            raise UpdateProcessingDatasetError

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(found_dataset, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        original_format = found_dataset.format
        new_format = serializer.validated_data.get("format", original_format)

        is_format_changed = new_format != original_format

        # Format change is not allowed if dataset already contains data
        if is_format_changed and found_dataset.data:
            raise DatasetFormatChangeError

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
