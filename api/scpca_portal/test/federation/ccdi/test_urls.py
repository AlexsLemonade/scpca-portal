"""Routing and toggle behavior for the CCDI federation node."""

from importlib import reload

from django.test import SimpleTestCase, override_settings
from django.urls import clear_url_caches
from rest_framework import status

import scpca_portal.urls
from scpca_portal.test.federation.ccdi.views import (
    test_file,
    test_info,
    test_metadata_fields,
    test_namespace,
    test_organization,
    test_sample,
    test_subject,
)

# Every node route, aggregated from the per-view test modules.
ALL_ENDPOINTS = (
    test_info.ENDPOINTS
    + test_namespace.ENDPOINTS
    + test_organization.ENDPOINTS
    + test_metadata_fields.ENDPOINTS
    + test_subject.ENDPOINTS
    + test_sample.ENDPOINTS
    + test_file.ENDPOINTS
)


class CCDIToggleTests(SimpleTestCase):
    def test_routes_present_when_enabled(self):
        # Test settings inherit ENABLE_FEATURE_PREVIEW = True from Common.
        # A registered route returns a non-404 status; 404 would mean it's unmounted.
        response = self.client.get("/federation/ccdi/v1/info")
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_routes_absent_when_disabled(self):
        try:
            with override_settings(ENABLE_FEATURE_PREVIEW=False):
                # The urlconf is evaluated at import time, so the setting change
                # only takes effect after the module is re-imported.
                clear_url_caches()
                reload(scpca_portal.urls)
                response = self.client.get("/federation/ccdi/v1/info")
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        finally:
            # Settings are restored when the `with` block exits; rebuild the real
            # urlconf so later tests see the node routes again.
            clear_url_caches()
            reload(scpca_portal.urls)


class CCDISurfaceTests(SimpleTestCase):
    def test_all_endpoints_are_routed(self):
        for url in ALL_ENDPOINTS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
