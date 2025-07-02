from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from rest_framework_extensions.mixins import NestedViewSetMixin

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.enums import JobStates
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

    def list(self, request):
        queryset = Dataset.objects.filter(is_ccdl=True)
        serializer = DatasetSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        token_id = self.request.META.get("HTTP_API_KEY")
        if not token_id or not APIToken.verify(token_id):
            raise PermissionDenied(
                {"message": "Your token is not valid or not activated.", "token_id": token_id}
            )

        serializer = DatasetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        dataset = serializer.save()

        if dataset.start:
            dataset_job = Job.get_dataset_job(dataset)
            try:
                dataset_job.submit()
            except Exception:
                logger.info(f"{dataset} job (attempt {dataset_job.attempt}) is being requeued.")
                dataset_job.attempt += 1
                if dataset_job.attempt > common.MAX_JOB_ATTEMPTS:
                    dataset_job.state = JobStates.FAILED
                    dataset_job.update_state_at()
                dataset_job.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = Dataset.objects.all()
        dataset = get_object_or_404(queryset, pk=pk)
        serializer = DatasetDetailSerializer(dataset, many=False)
        return Response(serializer.data)

    def update(self, request, pk=None):
        token_id = self.request.META.get("HTTP_API_KEY")
        if not token_id or not APIToken.verify(token_id):
            raise PermissionDenied(
                {"message": "Your token is not valid or not activated.", "token_id": token_id}
            )

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
            try:
                dataset_job.submit()
            except Exception:
                logger.info(
                    f"{modified_dataset} job (attempt {dataset_job.attempt}) is being requeued."
                )
                dataset_job.attempt += 1
                if dataset_job.attempt > common.MAX_JOB_ATTEMPTS:
                    dataset_job.state = JobStates.FAILED
                    dataset_job.update_state_at()
                dataset_job.save()

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
