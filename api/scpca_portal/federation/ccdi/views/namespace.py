"""
Namespace endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/supporting/namespace.html
"""

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from scpca_portal.federation.ccdi import config
from scpca_portal.federation.ccdi.schema import NamespaceResponse, NamespacesResponse
from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin


class NamespaceViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """/namespace — namespaces served by this node."""

    def list(self, request):
        namespaces = NamespacesResponse.model_validate([config.NAMESPACE])
        return Response(namespaces.model_dump(mode="json", by_alias=True))

    def retrieve(self, request, organization=None, namespace=None):
        identifier = config.NAMESPACE["id"]
        if organization != identifier["organization"] or namespace != identifier["name"]:
            raise NotFound()
        found = NamespaceResponse.model_validate(config.NAMESPACE)
        return Response(found.model_dump(mode="json", by_alias=True))
