"""Response tests for the /subject endpoints (burndown until implemented)."""

from unittest import expectedFailure

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/subject",
    "/federation/ccdi/subject/by/sex/count",
    "/federation/ccdi/subject/summary",
    "/federation/ccdi/subject/alsf/scpca/SUBJECT1",
    "/federation/ccdi/subject-diagnosis",
)


class SubjectViewTests(SimpleTestCase):
    @expectedFailure
    def test_endpoints_implemented(self):
        # Expected-fails (501) until the endpoints return real responses;
        # convert to real content assertions once implemented.
        for url in ENDPOINTS:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
