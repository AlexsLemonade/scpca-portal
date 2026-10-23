"""Shared base classes for the CCDI federation node views."""

from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny


class EndpointNotImplemented(APIException):
    """Raised by endpoints that are routed but whose response isn't built yet."""

    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "This CCDI node endpoint is not implemented yet."
    default_code = "not_implemented"


class CCDINodeViewMixin:
    """Shared config for node views: a public, unauthenticated discovery API."""

    authentication_classes: list = []
    permission_classes = [AllowAny]


class EntityViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """
    Shared endpoint surface for the CCDI primary entities (subject/sample/file):
    list, retrieve, by/{field}/count, and summary. Stubbed for now; the shared
    list/count/summary handling will live here once responses are implemented.
    """

    def list(self, request):
        raise EndpointNotImplemented()

    def retrieve(self, request, organization=None, namespace=None, name=None):
        raise EndpointNotImplemented()

    def count(self, request, field=None):
        """GET /{entity}/by/{field}/count"""
        raise EndpointNotImplemented()

    def summary(self, request):
        """GET /{entity}/summary"""
        raise EndpointNotImplemented()
