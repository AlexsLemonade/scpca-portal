"""
Serves the pinned CCDI Federation API OpenAPI document.

The document is the vendored upstream contract with `servers` overridden to
point at this node, so Swagger/Redoc "Try it out" targets us rather than the
reference nodes the spec lists. It is not a schema generated from our views.
"""

from pathlib import Path

from django.http import HttpResponse
from rest_framework.views import APIView

import yaml

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin

SPEC_PATH = Path(__file__).resolve().parent.parent / "swagger.yml"

# Relative so it resolves against the serving origin in any environment; the
# spec's paths (/subject, /info, …) then resolve under /federation/ccdi/v1/.
NODE_SERVERS = [{"url": "/federation/ccdi/v1", "description": "ScPCA CCDI node"}]


class SchemaView(CCDINodeViewMixin, APIView):
    """GET /docs/schema — the vendored CCDI OpenAPI document, scoped to this node."""

    def get(self, request):
        document = yaml.safe_load(SPEC_PATH.read_bytes())
        document["servers"] = NODE_SERVERS
        return HttpResponse(
            yaml.safe_dump(document, sort_keys=False), content_type="application/yaml"
        )
