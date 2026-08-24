"""Response tests for the /metadata/fields endpoints (burndown until implemented)."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/v1/metadata/fields/subject",
    "/federation/ccdi/v1/metadata/fields/sample",
    "/federation/ccdi/v1/metadata/fields/file",
)


class MetadataFieldsViewTests(SimpleTestCase):
    @expectedFailure
    def test_endpoints_implemented(self):
        # Expected-fails (501) until the endpoints return real responses;
        # convert to real content assertions once implemented.
        for url in ENDPOINTS:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
