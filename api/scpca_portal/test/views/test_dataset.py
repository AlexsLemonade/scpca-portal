from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import DatasetFactory


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    def setUp(self):
        self.project = DatasetFactory()

    def test_get_list(self):
        response = self.client.get(reverse("datasets-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
