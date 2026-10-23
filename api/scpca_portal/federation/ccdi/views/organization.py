"""
Organization endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/supporting/organization.html
"""

from rest_framework import viewsets
from rest_framework.response import Response

from scpca_portal.federation.ccdi import config, schema
from scpca_portal.federation.ccdi.schema import OrganizationResponse, OrganizationsResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin
from scpca_portal.federation.ccdi.views.errors import NotFound


class OrganizationViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """/organization — organizations served by this node."""

    def list(self, request):
        organizations = OrganizationsResponse.model_validate([config.ORGANIZATION])
        return Response(schema.dump(organizations))

    def retrieve(self, request, name=None):
        if name != config.ORGANIZATION["identifier"]:
            raise NotFound(f"Organization '{name}'")
        organization = OrganizationResponse.model_validate(config.ORGANIZATION)
        return Response(schema.dump(organization))
