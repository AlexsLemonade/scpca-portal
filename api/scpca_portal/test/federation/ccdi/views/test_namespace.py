"""Response tests for the /namespace endpoints."""

from django.test import SimpleTestCase
from rest_framework import status

from scpca_portal.federation.ccdi.schema import NamespaceResponse, NamespacesResponse

ENDPOINTS = (
    "/federation/ccdi/v1/namespace",
    "/federation/ccdi/v1/namespace/alsf/scpca",
)


class NamespaceViewTests(SimpleTestCase):
    def test_list_returns_a_valid_response(self):
        response = self.client.get("/federation/ccdi/v1/namespace")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        NamespacesResponse.model_validate(response.json())

    def test_detail_returns_a_valid_response(self):
        response = self.client.get("/federation/ccdi/v1/namespace/alsf/scpca")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        NamespaceResponse.model_validate(response.json())

    def test_unknown_namespace_is_not_found(self):
        response = self.client.get("/federation/ccdi/v1/namespace/alsf/unknown")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
