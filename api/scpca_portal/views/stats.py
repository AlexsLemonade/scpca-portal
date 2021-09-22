from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from scpca_portal.models import Project, Sample


@cache_page(None)
@api_view()
def stats_view(request):
    cancer_types_queryset = Sample.objects.order_by().values_list("diagnosis", flat=True).distinct()
    response_dict = {
        "projects": Project.objects.count(),
        "samples": Sample.objects.count(),
        "cancer_types": list(cancer_types_queryset),
        "cancer_types_count": cancer_types_queryset.count(),
        "labs": Project.objects.values("pi_name").distinct().count(),
    }
    return Response(response_dict)
