"""
Info endpoint for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/specification.html
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from scpca_portal.federation.ccdi import config
from scpca_portal.federation.ccdi.schema import InfoResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin


class InfoView(CCDINodeViewMixin, APIView):
    """GET /info — node metadata."""

    def get(self, request):
        info = InfoResponse.model_validate(config.INFO)
        return Response(info.model_dump(mode="json", by_alias=True))
