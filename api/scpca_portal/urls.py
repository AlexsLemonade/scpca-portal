from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView

from rest_framework_extensions.routers import ExtendedSimpleRouter

from scpca_portal.views import APITokenViewSet, ComputedFileViewSet, ProjectViewSet, SampleViewSet

router = ExtendedSimpleRouter()
router.trailing_slash = "/?"

router.register(r"computed-files", ComputedFileViewSet, basename="computed-files")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"samples", SampleViewSet, basename="samples")
router.register(r"tokens", APITokenViewSet, basename="tokens")

urlpatterns = [
    path("v1/", include(router.urls)),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
