from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import SampleComputedFileFactory, SampleFactory


class SamplesTestCase(APITestCase):
    """Tests /samples/ operations."""

    def setUp(self):
        self.sample = SampleFactory()
        computed_file = SampleComputedFileFactory()
        computed_file.sample = self.sample
        computed_file.save()

    def test_get_single(self):
        url = reverse("samples-detail", args=[self.sample.scpca_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get(reverse("samples-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = response.json()
        self.assertEqual(json_response["count"], 1)
        self.assertIn("size_in_bytes", json_response["results"][0]["computed_files"][0])

    def test_post_is_not_allowed(self):
        url = reverse("samples-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("samples-detail", args=[self.sample.scpca_id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("samples-detail", args=[self.sample.scpca_id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
