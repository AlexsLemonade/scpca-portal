"""
Organization endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/supporting/organization.html
"""

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from scpca_portal.federation.ccdi import config
from scpca_portal.federation.ccdi.schema import OrganizationResponse, OrganizationsResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin


class OrganizationViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """/organization — organizations served by this node."""

    def list(self, request):
        organizations = OrganizationsResponse.model_validate([config.ORGANIZATION])
        return Response(organizations.model_dump(mode="json", by_alias=True))

    def retrieve(self, request, name=None):
        if name != config.ORGANIZATION["identifier"]:
            raise NotFound()
        organization = OrganizationResponse.model_validate(config.ORGANIZATION)
        return Response(organization.model_dump(mode="json", by_alias=True))
