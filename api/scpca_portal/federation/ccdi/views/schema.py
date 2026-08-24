"""
Serves the vendored CCDI Federation API OpenAPI document.

The node's schema is the pinned upstream contract served verbatim, not a
schema generated from our views.
"""

from pathlib import Path

from django.http import HttpResponse
from rest_framework.views import APIView

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin

SPEC_PATH = Path(__file__).resolve().parent.parent / "swagger.yml"


class SchemaView(CCDINodeViewMixin, APIView):
    """GET /docs/schema — the vendored CCDI OpenAPI document."""

    def get(self, request):
        return HttpResponse(SPEC_PATH.read_bytes(), content_type="application/yaml")
