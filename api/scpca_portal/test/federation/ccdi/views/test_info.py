"""Response tests for the /info endpoint."""

from django.test import SimpleTestCase
from rest_framework import status

from scpca_portal.federation.ccdi.schema import InfoResponse

ENDPOINTS = ("/federation/ccdi/v1/info",)


class InfoViewTests(SimpleTestCase):
    def test_info_returns_a_valid_response(self):
        response = self.client.get(ENDPOINTS[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Round-trips into the generated response type → schema-valid.
        InfoResponse.model_validate(response.json())
