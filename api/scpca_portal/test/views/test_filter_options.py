from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ProjectFactory, SampleFactory

fake = Faker()


class FilterOptionsTestCase(APITestCase):
    """
    Tests /address list operations.
    """

    def setUp(self):
        self.project = ProjectFactory()
        SampleFactory(
            project=self.project,
            technologies="10Xv4, 10Xv5",
            seq_units="cell, bulk",
            diagnosis="different",
        )

    def test_get(self):
        url = reverse("project-options")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(len(response_json["diagnoses"]), 2)
        self.assertEqual(len(response_json["seq_units"]), 2)
        self.assertEqual(len(response_json["technologies"]), 3)
