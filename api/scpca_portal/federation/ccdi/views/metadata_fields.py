"""
Metadata fields endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/metadata.html
"""

from rest_framework.views import APIView

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin, EndpointNotImplemented


class MetadataFieldsView(CCDINodeViewMixin, APIView):
    """GET /metadata/fields/{subject,sample,file} — described metadata fields."""

    def get(self, request, entity=None):
        raise EndpointNotImplemented()
