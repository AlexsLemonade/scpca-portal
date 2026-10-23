"""Response tests for the /organization endpoints."""

from django.test import SimpleTestCase
from rest_framework import status

from scpca_portal.federation.ccdi.schema import OrganizationResponse, OrganizationsResponse

ENDPOINTS = (
    "/federation/ccdi/v1/organization",
    "/federation/ccdi/v1/organization/alsf",
)


class OrganizationViewTests(SimpleTestCase):
    def test_list_returns_a_valid_response(self):
        response = self.client.get("/federation/ccdi/v1/organization")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        OrganizationsResponse.model_validate(response.json())

    def test_detail_returns_a_valid_response(self):
        response = self.client.get("/federation/ccdi/v1/organization/alsf")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        OrganizationResponse.model_validate(response.json())

    def test_unknown_organization_is_not_found(self):
        response = self.client.get("/federation/ccdi/v1/organization/unknown")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
