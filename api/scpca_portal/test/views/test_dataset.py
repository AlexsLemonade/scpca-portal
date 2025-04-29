from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import DatasetFactory


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    def setUp(self):
        self.ccdl_dataset = DatasetFactory(is_ccdl=True)
        self.custom_dataset = DatasetFactory(is_ccdl=False)

    def test_get_single(self):
        url = reverse("datasets-detail", args=[self.ccdl_dataset.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_list(self):
        url = reverse("datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response.json()["count"], 1)
        self.assertNotEqual(response_json["results"][0].get("id"), str(self.custom_dataset.id))
        self.assertEqual(response_json["results"][0].get("id"), str(self.ccdl_dataset.id))

    def test_post_is_not_allowed(self):
        url = reverse("datasets-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
