"""
File entity endpoints for the CCDI federation node.

See: https://cbiit.github.io/ccdi-federation-api/entities/primary/file.html
"""

from scpca_portal.federation.ccdi.views.base import EntityViewSet


class FileViewSet(EntityViewSet):
    """/file endpoints."""
