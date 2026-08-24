"""Response tests for the /file endpoints (burndown until implemented)."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/v1/file",
    "/federation/ccdi/v1/file/by/type/count",
    "/federation/ccdi/v1/file/summary",
    "/federation/ccdi/v1/file/alsf/scpca/FILE1",
)


class FileViewTests(SimpleTestCase):
    @expectedFailure
    def test_endpoints_implemented(self):
        # Expected-fails (501) until the endpoints return real responses;
        # convert to real content assertions once implemented.
        for url in ENDPOINTS:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
