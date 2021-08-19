from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ProcessorFactory

fake = Faker()


class ProcessorsTestCase(APITestCase):
    """
    Tests /processors/ operations.
    """

    def setUp(self):
        self.processor = ProcessorFactory()

    def test_get_single(self):
        url = reverse("processors-detail", args=[self.processor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get(reverse("processors-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_post_is_not_allowed(self):
        url = reverse("processors-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("processors-detail", args=[self.processor.id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("processors-detail", args=[self.processor.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
