"""Response tests for the /sample endpoints (burndown until implemented)."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/sample",
    "/federation/ccdi/sample/by/disease_phase/count",
    "/federation/ccdi/sample/summary",
    "/federation/ccdi/sample/alsf/scpca/SAMPLE1",
    "/federation/ccdi/sample-diagnosis",
)


class SampleViewTests(SimpleTestCase):
    @expectedFailure
    def test_endpoints_implemented(self):
        # Expected-fails (501) until the endpoints return real responses;
        # convert to real content assertions once implemented.
        for url in ENDPOINTS:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
