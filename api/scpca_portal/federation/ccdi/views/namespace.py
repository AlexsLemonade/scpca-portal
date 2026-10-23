"""
Namespace endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/supporting/namespace.html
"""

from rest_framework import viewsets

from scpca_portal.federation.ccdi.views.base import CCDINodeViewMixin, EndpointNotImplemented


class NamespaceViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """/namespace — namespaces served by this node."""

    def list(self, request):
        raise EndpointNotImplemented()

    def retrieve(self, request, organization=None, namespace=None):
        raise EndpointNotImplemented()
