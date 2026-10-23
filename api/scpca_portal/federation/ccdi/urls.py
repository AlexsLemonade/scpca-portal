"""
URL routing for the CCDI Federation API node, mounted at `/federation/ccdi/`.

Paths mirror the CCDI v1.3.0 spec (no trailing slash). The node owns this
routing table directly rather than sharing the v1 router. Route order matters:
the specific `by/{field}/count`, `summary`, and top-level `-diagnosis` routes
are declared before the greedy 3-segment `{organization}/{namespace}/{name}`
detail route so they are not shadowed by it.
"""

from django.urls import path

from scpca_portal.federation.ccdi import views

app_name = "ccdi"

info_urls = [
    path("info", views.InfoView.as_view(), name="info"),
]

namespace_urls = [
    path("namespace", views.NamespaceViewSet.as_view({"get": "list"}), name="namespace-list"),
    path(
        "namespace/<str:organization>/<str:namespace>",
        views.NamespaceViewSet.as_view({"get": "retrieve"}),
        name="namespace-detail",
    ),
]

organization_urls = [
    path(
        "organization",
        views.OrganizationViewSet.as_view({"get": "list"}),
        name="organization-list",
    ),
    path(
        "organization/<str:name>",
        views.OrganizationViewSet.as_view({"get": "retrieve"}),
        name="organization-detail",
    ),
]

metadata_urls = [
    path(
        "metadata/fields/subject",
        views.MetadataFieldsView.as_view(),
        {"entity": "subject"},
        name="metadata-fields-subject",
    ),
    path(
        "metadata/fields/sample",
        views.MetadataFieldsView.as_view(),
        {"entity": "sample"},
        name="metadata-fields-sample",
    ),
    path(
        "metadata/fields/file",
        views.MetadataFieldsView.as_view(),
        {"entity": "file"},
        name="metadata-fields-file",
    ),
]

subject_urls = [
    path("subject", views.SubjectViewSet.as_view({"get": "list"}), name="subject-list"),
    path(
        "subject/by/<str:field>/count",
        views.SubjectViewSet.as_view({"get": "count"}),
        name="subject-count",
    ),
    path(
        "subject/summary",
        views.SubjectViewSet.as_view({"get": "summary"}),
        name="subject-summary",
    ),
    path(
        "subject-diagnosis",
        views.SubjectViewSet.as_view({"get": "diagnosis"}),
        name="subject-diagnosis",
    ),
    path(
        "subject/<str:organization>/<str:namespace>/<str:name>",
        views.SubjectViewSet.as_view({"get": "retrieve"}),
        name="subject-detail",
    ),
]

sample_urls = [
    path("sample", views.SampleViewSet.as_view({"get": "list"}), name="sample-list"),
    path(
        "sample/by/<str:field>/count",
        views.SampleViewSet.as_view({"get": "count"}),
        name="sample-count",
    ),
    path(
        "sample/summary",
        views.SampleViewSet.as_view({"get": "summary"}),
        name="sample-summary",
    ),
    path(
        "sample-diagnosis",
        views.SampleViewSet.as_view({"get": "diagnosis"}),
        name="sample-diagnosis",
    ),
    path(
        "sample/<str:organization>/<str:namespace>/<str:name>",
        views.SampleViewSet.as_view({"get": "retrieve"}),
        name="sample-detail",
    ),
]

file_urls = [
    path("file", views.FileViewSet.as_view({"get": "list"}), name="file-list"),
    path(
        "file/by/<str:field>/count",
        views.FileViewSet.as_view({"get": "count"}),
        name="file-count",
    ),
    path("file/summary", views.FileViewSet.as_view({"get": "summary"}), name="file-summary"),
    path(
        "file/<str:organization>/<str:namespace>/<str:name>",
        views.FileViewSet.as_view({"get": "retrieve"}),
        name="file-detail",
    ),
]

urlpatterns = (
    info_urls
    + namespace_urls
    + organization_urls
    + metadata_urls
    + subject_urls
    + sample_urls
    + file_urls
)
