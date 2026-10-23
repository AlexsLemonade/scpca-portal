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

    def describe(self, entity):
        url = f"/federation/ccdi/v1/metadata/fields/{entity}"

        return MetadataFieldsResponse.model_validate(self.client.get(url).json()).fields

    # One per entity rather than a loop: a shared tripwire would only flip once
    # all three were mapped, so the first entity's mappings would land with
    # nothing asserting them.
    @expectedFailure
    def test_subject_fields_are_described(self):
        self.assertNotEqual(self.describe("subject"), [])

    @expectedFailure
    def test_sample_fields_are_described(self):
        self.assertNotEqual(self.describe("sample"), [])

    @expectedFailure
    def test_file_fields_are_described(self):
        self.assertNotEqual(self.describe("file"), [])
