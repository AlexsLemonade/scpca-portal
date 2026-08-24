"""
Organization endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/supporting/organization.html
"""

from rest_framework import viewsets

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin, EndpointNotImplemented


class OrganizationViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """/organization — organizations served by this node."""

    def list(self, request):
        raise EndpointNotImplemented()

    def retrieve(self, request, name=None):
        raise EndpointNotImplemented()
