from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.response import Response

from scpca_portal.models import Project, Sample


class StatsViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(None))
    def list(self, request):
        cancer_types_field_name = "diagnosis"
        cancer_types_queryset = (
            Sample.objects.distinct(cancer_types_field_name)
            .order_by(cancer_types_field_name)  # Must match distinct expression.
            .values_list(cancer_types_field_name, flat=True)
        )

        return Response(
            {
                "cancer_types": list(cancer_types_queryset),
                "cancer_types_count": cancer_types_queryset.count(),
                "labs_count": Project.objects.values("pi_name").distinct().count(),
                "projects_count": Project.objects.count(),
                "samples_count": Sample.objects.filter(sample_computed_file__isnull=False).count(),
            }
        )
