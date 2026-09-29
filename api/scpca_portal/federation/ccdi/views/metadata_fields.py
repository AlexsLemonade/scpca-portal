"""
Metadata fields endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/metadata.html
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping.file import File
from scpca_portal.federation.ccdi.mapping.sample import Sample
from scpca_portal.federation.ccdi.mapping.subject import Subject
from scpca_portal.federation.ccdi.schema import MetadataFieldsResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin

# The routes carry the entity name, so this is the one place that maps a name
# back to its mappings; everything else imports the module it wants.
FIELD_MAPS = {entity.FIELDS.name: entity.FIELDS for entity in (Subject, Sample, File)}


class MetadataFieldsView(CCDINodeViewMixin, APIView):
    """GET /metadata/fields/{subject,sample,file} — described metadata fields."""

    def get(self, request, entity=None):
        described = MetadataFieldsResponse(fields=FIELD_MAPS[entity].describe())

        return Response(schema.dump(described))
