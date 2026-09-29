"""Response tests for the /file endpoints (burndown until implemented)."""

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/v1/file",
    "/federation/ccdi/v1/file/by/type/count",
    "/federation/ccdi/v1/file/summary",
    "/federation/ccdi/v1/file/alsf/scpca/FILE1",
)


class FileViewTests(SimpleTestCase):
    def test_pending_endpoints_are_still_stubs(self):
        """
        The burndown marker for `/file`.

        Asserts the *stub* state rather than the finished one, so it fails the
        moment an endpoint stops answering 501 — and fails by name. An
        `@expectedFailure` asserting 200 cannot do that job here: a detail route
        answers 404 for a name that does not exist, both before and after it is
        implemented, so such a test stays green forever.

        Every `/file` endpoint is still a stub, so this covers the whole
        surface. As one lands, split the implemented routes out of `ENDPOINTS`
        into a `PENDING_ENDPOINTS` list — `test_sample.py` shows the shape — and
        write real content assertions for it.
        """
        for url in ENDPOINTS:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_501_NOT_IMPLEMENTED)
