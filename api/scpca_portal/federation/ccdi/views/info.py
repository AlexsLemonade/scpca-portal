"""
Info endpoint for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/specification.html
"""

from rest_framework.views import APIView

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin, EndpointNotImplemented


class InfoView(CCDINodeViewMixin, APIView):
    """GET /info — node metadata."""

    def get(self, request):
        raise EndpointNotImplemented()
