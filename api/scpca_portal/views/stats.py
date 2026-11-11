from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import serializers, viewsets
from rest_framework.response import Response

from drf_spectacular.utils import OpenApiResponse, extend_schema

from scpca_portal.models import OriginalFile, Project

NON_CANCER_TYPES = ["Non-cancerous", "Normal margin", "Other"]


class StatsResponseSerializer(serializers.Serializer):
    cancer_types = serializers.ListField(child=serializers.CharField())
    cancer_types_count = serializers.IntegerField(min_value=0)
    labs_count = serializers.IntegerField(min_value=0)
    projects_count = serializers.IntegerField(min_value=0)
    samples_count = serializers.IntegerField(min_value=0)


class StatsViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(None))
    @extend_schema(
        auth=False,
        responses={
            200: OpenApiResponse(response=StatsResponseSerializer),
        },
    )
    def list(self, request):
        """
        Provides list of counts for projects, cancer types, total samples,
        and labs available on the portal.
        """
        cancer_types_count = len(
            {
                diagnosis
                for diagnoses in Project.objects.values_list("diagnoses", flat=True)
                for diagnosis in diagnoses
                if diagnosis not in NON_CANCER_TYPES
            }
        )

        return Response(
            {
                "cancer_types_count": cancer_types_count,
                "labs_count": Project.objects.values("pi_name").distinct().count(),
                "projects_count": Project.objects.count(),
                "samples_count": len(
                    set().union(
                        *OriginalFile.downloadable_objects.order_by().values_list(
                            "sample_ids", flat=True
                        )
                    )
                ),
            }
        )
