from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import serializers, viewsets
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse

from scpca_portal.models import Project, Sample

NON_CANCER_TYPES = ["Non-cancerous", "Normal margin"]


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
        Provides list of all cancer types as well as counts for cancer types,
        labs, projects, and samples accounted for on the portal.
        """
        cancer_types_field_name = "diagnosis"
        cancer_types_queryset = (
            Sample.objects.distinct(cancer_types_field_name)
            .exclude(diagnosis__in=NON_CANCER_TYPES)
            .order_by(cancer_types_field_name)  # Must match distinct expression.
            .values_list(cancer_types_field_name, flat=True)
        )

        return Response(
            {
                "cancer_types": list(cancer_types_queryset),
                "cancer_types_count": cancer_types_queryset.count(),
                "labs_count": Project.objects.values("pi_name").distinct().count(),
                "projects_count": Project.objects.count(),
                "samples_count": Sample.objects.filter(sample_computed_files__isnull=False)
                .distinct()
                .count(),
            }
        )
