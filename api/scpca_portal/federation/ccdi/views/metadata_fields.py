"""
Metadata fields endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/metadata.html
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from scpca_portal.federation.ccdi import config
from scpca_portal.federation.ccdi.schema import MetadataFieldsResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin


class MetadataFieldsView(CCDINodeViewMixin, APIView):
    """GET /metadata/fields/{subject,sample,file} — described metadata fields."""

    def get(self, request, entity=None):
        fields = MetadataFieldsResponse.model_validate(config.METADATA_FIELDS[entity])
        return Response(fields.model_dump(mode="json", by_alias=True))
