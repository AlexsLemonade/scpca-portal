from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from scpca_portal.models import Project, Sample


@cache_page(None)
@api_view()
def stats_view(request):
    response_dict = {
        "projects": Project.objects.count(),
        "samples": Sample.objects.count(),
        "cancer_types": Sample.objects.values("diagnosis").distinct().count(),
        "labs": Project.objects.values("pi_name").distinct().count(),
    }
    return Response(response_dict)
