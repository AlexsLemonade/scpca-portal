from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.exceptions import DatasetError, JobError
from scpca_portal.models import APIToken, Dataset, Job
from scpca_portal.serializers import (
    DatasetCreateSerializer,
    DatasetDetailSerializer,
    DatasetSerializer,
    DatasetUpdateSerializer,
)

logger = get_and_configure_logger(__name__)


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    ordering_fields = "__all__"

    # TODO: Either add serializer_class/queryset to the class or use viewsets.ViewSet
    # Fixes browser error 500 (not caught by tests) by setting default serializer and queryset
    # https://www.django-rest-framework.org/api-guide/generic-views/#examples
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filterset_fields = (
        "id",
        "is_ccdl",
        "ccdl_name",
        "ccdl_project_id",
        "format",
        # data  # TODO: consider if we want to query for modality on CCDL datasets
        # or included project ids, modalities, and bulk in custom datasets
        # TODO: decide if we want to allow querying on is_state attributes
    )

    def get_and_validate_token(self, request) -> APIToken:
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

        return token

    def list(self, request):
        queryset = Dataset.objects.all()
        # if custom datasets are requested (with is_ccdl set to false), then a token must be present
        if request.query_params.get("is_ccdl").lower() == "false":
            token = self.get_and_validate_token(request)
            queryset = queryset.filter(is_ccdl=False, token=token)
        # ccdl datasets are queried when the is_ccdl param is set
        # and by default if no is_ccdl param is passed
        else:
            queryset = queryset.filter(is_ccdl=True)

        serializer = DatasetSerializer(self.filter_queryset(queryset), many=True)
        return Response(serializer.data)

    def create(self, request):
        self.get_and_validate_token(request)

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

    def retrieve(self, request, pk=None):
        queryset = Dataset.objects.all()
        dataset = get_object_or_404(queryset, pk=pk)
        if not dataset.is_ccdl:
            self.get_and_validate_token(request)

        serializer = DatasetDetailSerializer(dataset, many=False)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = Dataset.objects.all()
        existing_dataset = get_object_or_404(queryset, pk=pk)
        if not existing_dataset.is_ccdl:
            self.get_and_validate_token(request)

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
