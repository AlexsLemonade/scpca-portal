"""
Every failure the node produces answers with the spec's `responses.Errors`.

Each case asserts the `kind` and the body's validity, not just the status code —
a status alone would pass for DRF's `{"detail": …}`, which is what these exist
to stop.
"""

from django.test import Client, SimpleTestCase, TestCase
from rest_framework import status

from scpca_portal.federation.ccdi.schema import ErrorsResponse
from scpca_portal.test.federation.ccdi.views.test_sample import build_pair, detail_url

NODE = "/federation/ccdi/v1"


def only_error(response):
    """The single error in a node failure, after checking the body validates."""
    body = response.json()
    ErrorsResponse.model_validate(body)

    assert len(body["errors"]) == 1, body
    return body["errors"][0]


class InvalidRouteTests(SimpleTestCase):
    """
    No endpoint matches. 404 either way, including for a wrong method — the
    spec documents `InvalidRoute` as covering "all routes for which the path
    exists, but the HTTP method is not supported for that path".
    """

    def test_a_path_under_the_node_that_matches_no_endpoint(self):
        response = self.client.get(f"{NODE}/samples")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            only_error(response),
            {
                "kind": "InvalidRoute",
                "method": "GET",
                "route": f"{NODE}/samples",
                "message": f"Invalid route: GET {NODE}/samples.",
            },
        )

    def test_a_method_the_endpoint_does_not_support(self):
        response = self.client.post(f"{NODE}/sample")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(only_error(response)["kind"], "InvalidRoute")
        self.assertEqual(only_error(response)["method"], "POST")

    def test_an_unsafe_method_on_an_unrouted_path_is_not_a_csrf_failure(self):
        # The catch-all is a plain Django view, so CSRF middleware runs on it —
        # DRF views are exempt by default and this one is not. Without the
        # exemption this answers Django's 403 HTML page. The default test client
        # does not enforce CSRF, so it cannot see this.
        response = Client(enforce_csrf_checks=True).post(f"{NODE}/samples")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(only_error(response)["kind"], "InvalidRoute")

    def test_the_docs_routes_are_not_swallowed_by_the_catch_all(self):
        # The catch-all is last, so everything above it still resolves.
        for path in ("/federation/ccdi/docs/schema", "/federation/ccdi/"):
            with self.subTest(path=path):
                self.assertNotEqual(self.client.get(path).status_code, status.HTTP_404_NOT_FOUND)


class NotFoundTests(TestCase):
    """A route that exists, for a record that does not."""

    def test_an_unknown_sample_name(self):
        response = self.client.get(detail_url("SCPCL999999-SCPCS999999"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        error = only_error(response)
        self.assertEqual(error["kind"], "NotFound")
        self.assertIn("SCPCL999999-SCPCS999999", error["entity"])
        self.assertTrue(error["message"].endswith("not found."))

    def test_a_namespace_that_is_not_ours(self):
        # The record has to exist under our namespace, or the 404 comes from the
        # lookup rather than the namespace guard — and both raise `NotFound`, so
        # only the entity string tells them apart.
        library, sample = build_pair()
        name = f"{library.scpca_id}-{sample.scpca_id}"

        response = self.client.get(f"{NODE}/sample/other/elsewhere/{name}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(only_error(response)["entity"], "Sample in namespace 'other/elsewhere'")

    def test_that_same_sample_resolves_under_our_own_namespace(self):
        # Keeps the test above honest: it is the namespace that was rejected.
        library, sample = build_pair()

        response = self.client.get(detail_url(f"{library.scpca_id}-{sample.scpca_id}"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_an_unknown_organization(self):
        response = self.client.get(f"{NODE}/organization/nope")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(only_error(response)["entity"], "Organization 'nope'")

    def test_an_unknown_namespace(self):
        response = self.client.get(f"{NODE}/namespace/nope/nope")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(only_error(response)["kind"], "NotFound")


class InvalidParametersTests(TestCase):
    def test_a_page_no_offset_can_be_calculated_from(self):
        response = self.client.get(f"{NODE}/sample", {"page": 0})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        error = only_error(response)
        self.assertEqual(error["kind"], "InvalidParameters")
        self.assertEqual(error["parameters"], ["page", "per_page"])
        self.assertIn("offset", error["reason"])

    def test_the_message_names_the_parameters_at_fault(self):
        response = self.client.get(f"{NODE}/sample", {"per_page": "many"})

        self.assertIn("'page' and 'per_page'", only_error(response)["message"])

    def test_the_reason_stands_alone_as_a_sentence(self):
        # It is a field in its own right, so it cannot be a fragment that only
        # parses when interpolated into `message`.
        reason = only_error(self.client.get(f"{NODE}/sample", {"page": 0}))["reason"]

        self.assertTrue(reason[0].isupper(), reason)
        self.assertTrue(reason.endswith("."), reason)


class ContentTypeTests(TestCase):
    """
    The spec declares `application/json` for every response it documents and no
    other media type, so the node's API views are pinned to it. Without that,
    a browser gets DRF's browsable-API page instead of the error body.
    """

    BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

    def test_a_browser_gets_the_error_body_rather_than_the_browsable_api(self):
        response = self.client.get(f"{NODE}/organization/nope", HTTP_ACCEPT=self.BROWSER)

        self.assertEqual(response["content-type"], "application/json")
        self.assertEqual(only_error(response)["kind"], "NotFound")

    def test_the_docs_route_still_serves_a_client_that_wants_html(self):
        # The docs routes are ours, not the spec's, so HTML there is legitimate
        # and must not be answered with a 406.
        response = self.client.get("/federation/ccdi/docs/schema", HTTP_ACCEPT="text/html")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ScopeTests(TestCase):
    """The handler is scoped by inheritance, so v1 must be untouched."""

    def test_a_wrong_method_on_v1_is_still_a_405(self):
        """
        The leak that scoping actually prevents.

        `MethodNotAllowed` is translated to `InvalidRoute` unconditionally, so a
        globally installed handler would turn every v1 405 into a CCDI-shaped
        404. Nothing else the handler does is visible outside the node, which
        makes this the one case worth asserting.
        """
        response = self.client.post("/v1/projects")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn("detail", response.json())

    def test_a_v1_path_that_matches_nothing_is_not_caught_by_the_catch_all(self):
        response = self.client.get("/v1/nothing-here")

        self.assertNotIn("application/json", response.get("content-type", ""))
