from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import LeafProjectFactory, ProjectFactory, SampleFactory

fake = Faker()


class FilterOptionsTestCase(APITestCase):
    """
    Tests /options/projects/ endpoint
    """

    def setUp(self):
        self.project = ProjectFactory()
        SampleFactory(
            project=self.project,
            technologies="10Xv4, 10Xv5",
            seq_units="cell, bulk",
            diagnosis="different",
        )

        # Create an Project with no Samples:
        LeafProjectFactory()

    def test_get(self):
        url = reverse("project-options-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()

        self.assertEqual(len(response_json["diagnoses"]), 4)
        self.assertEqual(len(response_json["seq_units"]), 2)
        self.assertEqual(len(response_json["technologies"]), 5)
