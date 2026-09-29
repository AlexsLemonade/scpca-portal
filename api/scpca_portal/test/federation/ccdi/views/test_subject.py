"""Response tests for the /subject endpoints (burndown until implemented)."""

from django.test import SimpleTestCase
from rest_framework import status

ENDPOINTS = (
    "/federation/ccdi/v1/subject",
    "/federation/ccdi/v1/subject/by/sex/count",
    "/federation/ccdi/v1/subject/summary",
    "/federation/ccdi/v1/subject/alsf/scpca/SUBJECT1",
    "/federation/ccdi/v1/subject-diagnosis",
)


class SubjectViewTests(SimpleTestCase):
    def test_pending_endpoints_are_still_stubs(self):
        """
        The burndown marker for `/subject`.

        Asserts the *stub* state rather than the finished one, so it fails the
        moment an endpoint stops answering 501 — and fails by name. An
        `@expectedFailure` asserting 200 cannot do that job here: a detail route
        answers 404 for a name that does not exist, both before and after it is
        implemented, so such a test stays green forever.

        Every `/subject` endpoint is still a stub, so this covers the whole
        surface. As one lands, split the implemented routes out of `ENDPOINTS`
        into a `PENDING_ENDPOINTS` list — `test_sample.py` shows the shape — and
        write real content assertions for it.
        """
        for url in ENDPOINTS:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_501_NOT_IMPLEMENTED)
