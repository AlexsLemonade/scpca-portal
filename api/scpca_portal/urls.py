from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_extensions.routers import ExtendedDefaultRouter

from scpca_portal.views import (
    APITokenViewSet,
    ComputedFileViewSet,
    DatasetViewSet,
    FilterOptionsViewSet,
    ProjectViewSet,
    SampleViewSet,
    StatsViewSet,
)

schema_view = get_schema_view(
    openapi.Info(
        title="ScPCA Portal API",
        default_version="v1",
        description="""
The Single-cell Pediatric Cancer Atlas is a collection of pediatric cancer projects that collected single-cell sequencing data and were processed using the workflows contained in https://github.com/AlexsLemonade/alsf-scpca.

The swagger-ui view can be found [here](http://api.scpca.alexslemonade.org/v1/swagger/).

The ReDoc view can be found [here](https://api.scpca.alexslemonade.org/v1/redoc/).

Additional documentation can be found at [scpca.readthedocs.io](https://scpca.readthedocs.io/en/latest/).

### Questions/Feedback?

If you have a question or comment, please [file an issue on GitHub](https://github.com/AlexsLemonade/scpca-portal/issues) or send us an email at [requests@ccdatalab.org](mailto:requests@ccdatalab.org).
        """,
        terms_of_service="https://scpca.alexslemonade.org/terms-of-use",
        contact=openapi.Contact(email="requests@ccdatalab.org"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="https://api.scpca.alexslemonade.org",
)

router = ExtendedDefaultRouter()
router.trailing_slash = "/?"

router.register(r"computed-files", ComputedFileViewSet, basename="computed-files")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"samples", SampleViewSet, basename="samples")
router.register(r"tokens", APITokenViewSet, basename="tokens")
router.register(r"project-options", FilterOptionsViewSet, basename="project-options")
router.register(r"stats", StatsViewSet, basename="stats")

# Datasets are not ready for prime time yet.
if not settings.PRODUCTION:
    router.register(r"datasets", DatasetViewSet, basename="datasets")

urlpatterns = [
    path(
        "v1/",
        include(
            router.urls
            + [
                re_path(
                    r"^swagger/$",
                    schema_view.with_ui("swagger", cache_timeout=0),
                    name="schema_swagger_ui",
                ),
                re_path(
                    r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema_redoc"
                ),
            ]
        ),
    ),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
