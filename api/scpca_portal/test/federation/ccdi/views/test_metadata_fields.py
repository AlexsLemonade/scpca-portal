"""Response tests for the /metadata/fields endpoints."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

from scpca_portal.federation.ccdi.schema import MetadataFieldsResponse

ENDPOINTS = (
    "/federation/ccdi/v1/metadata/fields/subject",
    "/federation/ccdi/v1/metadata/fields/sample",
    "/federation/ccdi/v1/metadata/fields/file",
)


class MetadataFieldsViewTests(SimpleTestCase):
    def test_endpoints_return_valid_responses(self):
        for url in ENDPOINTS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                MetadataFieldsResponse.model_validate(response.json())

    @expectedFailure
    def test_endpoints_describe_fields(self):
        # Empty until the metadata mapping populates field descriptions; this
        # flips to an unexpected success once it does, prompting a real assertion.
        for url in ENDPOINTS:
            with self.subTest(url=url):
                fields = MetadataFieldsResponse.model_validate(self.client.get(url).json()).fields
                self.assertNotEqual(fields, [])
