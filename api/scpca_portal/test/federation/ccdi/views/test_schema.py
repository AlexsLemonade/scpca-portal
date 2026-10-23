"""Tests for the served CCDI node OpenAPI schema and its docs UIs."""

from pathlib import Path

from django.test import SimpleTestCase
from rest_framework import status

import yaml

from scpca_portal.federation import ccdi
from scpca_portal.federation.ccdi.views.schema import NODE_SERVERS

VENDORED_SPEC = Path(ccdi.__file__).parent / "swagger.yml"


class SchemaViewTests(SimpleTestCase):
    def served_document(self):
        response = self.client.get("/federation/ccdi/docs/schema")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return yaml.safe_load(response.content)

    def test_served_schema_is_v1_3_0(self):
        self.assertEqual(self.served_document()["info"]["version"], "v1.3.0")

    def test_served_schema_targets_this_node(self):
        self.assertEqual(self.served_document()["servers"], NODE_SERVERS)

    def test_served_schema_matches_vendored_spec_except_servers(self):
        served = self.served_document()
        vendored = yaml.safe_load(VENDORED_SPEC.read_bytes())
        served.pop("servers", None)
        vendored.pop("servers", None)
        self.assertEqual(served, vendored)

    def test_docs_uis_render(self):
        for url in ("/federation/ccdi/docs/swagger", "/federation/ccdi/docs/redoc"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
