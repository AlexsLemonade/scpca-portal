from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from scpca_portal.views import (
    APITokenViewSet,
    CCDLDatasetViewSet,
    ComputedFileViewSet,
    DatasetViewSet,
    FilterOptionsViewSet,
    ProjectViewSet,
    SampleViewSet,
    StatsViewSet,
)

router = ExtendedDefaultRouter()
router.trailing_slash = "/?"

router.register(r"ccdl-datasets", CCDLDatasetViewSet, basename="ccdl-datasets")
router.register(r"datasets", DatasetViewSet, basename="datasets")
router.register(r"computed-files", ComputedFileViewSet, basename="computed-files")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"samples", SampleViewSet, basename="samples")
router.register(r"tokens", APITokenViewSet, basename="tokens")
router.register(r"project-options", FilterOptionsViewSet, basename="project-options")
router.register(r"stats", StatsViewSet, basename="stats")

urlpatterns = [
    path(
        "v1/",
        include(
            router.urls
            + [
                path(r"schema/", SpectacularAPIView.as_view(), name="schema"),
            ]
        ),
    ),
    path(
        "docs/",
        include(
            [
                re_path(
                    r"^$", RedirectView.as_view(url=reverse_lazy("swagger-ui"), permanent=False)
                ),
                re_path(
                    r"^swagger/$",
                    SpectacularSwaggerView.as_view(url_name="schema"),
                    name="swagger-ui",
                ),
                re_path(
                    r"^redoc/$",
                    SpectacularRedocView.as_view(url_name="schema"),
                    name="redoc",
                ),
            ]
        ),
    ),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
