from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.response import Response

from scpca_portal.models import Project, Sample


class StatsViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(None))
    def list(self, request):
        cancer_types_queryset = (
            Sample.objects.order_by().values_list("diagnosis", flat=True).distinct()
        )
        response_dict = {
            "projects_count": Project.objects.count(),
            "samples_count": Sample.objects.count(),
            "cancer_types": list(cancer_types_queryset),
            "cancer_types_count": cancer_types_queryset.count(),
            "labs_count": Project.objects.values("pi_name").distinct().count(),
        }
        return Response(response_dict)
