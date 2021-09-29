from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ProjectFactory, SampleFactory

fake = Faker()


class StatsTestCase(APITestCase):
    """
    Tests /stats/ endpoint
    """

    def setUp(self):
        project = ProjectFactory()
        SampleFactory(
            project=project,
            technologies="10Xv4, 10Xv5",
            seq_units="cell, bulk",
            diagnosis="different",
        )

        ProjectFactory()
        ProjectFactory(pi_name="different")

    def test_get(self):
        url = reverse("stats-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response_json["projects_count"], 3)
        self.assertEqual(response_json["samples_count"], 4)
        self.assertEqual(response_json["cancer_types"], ["different", "pilocytic astrocytoma"])
        self.assertEqual(response_json["cancer_types_count"], 2)
        self.assertEqual(response_json["labs_count"], 2)
