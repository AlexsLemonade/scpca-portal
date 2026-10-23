"""
Sample entity endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/primary/sample.html
"""

from scpca_portal.federation.ccdi.views.base import EndpointNotImplemented, EntityViewSet


class SampleViewSet(EntityViewSet):
    """/sample endpoints."""

    def diagnosis(self, request):
        """GET /sample-diagnosis"""
        raise EndpointNotImplemented()
