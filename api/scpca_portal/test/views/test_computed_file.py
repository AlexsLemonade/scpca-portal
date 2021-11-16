import json
from unittest.mock import patch

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ComputedFileFactory

fake = Faker()


class MockS3Client:
    def __init__(self, *args, **kwargs):
        pass

    def generate_presigned_url(self, *args, **kwargs):
        return "This isn't really a presigned URL but it's good enough."


class ComputedFilesTestCase(APITestCase):
    """
    Tests /computed_files/ operations.
    """

    def setUp(self):
        self.computed_file = ComputedFileFactory()

    def test_options(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        # The presence of the origin header triggers CORS middleware,
        # but its content don't matter for this test.
        response = self.client.options(url, HTTP_ORIGIN="example.com")

        self.assertIn(
            settings.API_KEY_HEADER, response.get("Access-Control-Allow-Headers").split(", ")
        )

    def test_get_single(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn("download_url", response.json())

    @patch("scpca_portal.models.computed_file.s3", MockS3Client())
    def test_get_with_token(self):
        # create token
        response = self.client.post(
            reverse("tokens-list"),
            json.dumps({"is_activated": True, "email": "hi@example.com"}),
            content_type="application/json",
        )
        token_id = response.json()["id"]

        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.get(url, HTTP_API_KEY=token_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone("download_url", response.json())

    def test_get_with_bad_token(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.get(url, HTTP_API_KEY="bad token")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list(self):
        response = self.client.get(reverse("computed-files-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # One for self.computed_file, and one for
        # self.computed_file.sample.project.computed_file
        response_json = response.json()
        self.assertEqual(response_json["count"], 2)

        # Make sure there's no download_urls in list:
        self.assertNotIn("download_url", response_json["results"][0])

    def test_post_is_not_allowed(self):
        url = reverse("computed-files-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
