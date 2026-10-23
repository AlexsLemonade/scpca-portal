"""Response tests for the /namespace endpoints (burndown until implemented)."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/namespace",
    "/federation/ccdi/namespace/alsf/scpca",
)


class NamespaceViewTests(SimpleTestCase):
    @expectedFailure
    def test_endpoints_implemented(self):
        # Expected-fails (501) until the endpoints return real responses;
        # convert to real content assertions once implemented.
        for url in ENDPOINTS:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
