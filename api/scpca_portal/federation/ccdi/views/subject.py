"""
Subject entity endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/primary/subject.html
"""

from scpca_portal.federation.ccdi.views.base import EndpointNotImplemented, EntityViewSet


class SubjectViewSet(EntityViewSet):
    """/subject endpoints."""

    def diagnosis(self, request):
        """GET /subject-diagnosis"""
        raise EndpointNotImplemented()
