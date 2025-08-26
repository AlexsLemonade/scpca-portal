from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import ProjectFactory, SampleFactory


class StatsTestCase(APITestCase):
    """Tests /stats/ endpoint."""

    def setUp(self):
        ProjectFactory()
        ProjectFactory(pi_name="different")
        SampleFactory(
            diagnosis="different",
            project=ProjectFactory(),
            seq_units=["cell", "bulk"],
            technologies=["10Xv4", "10Xv5"],
        )

    def test_get(self):
        response = self.client.get(reverse("stats-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response_json["cancer_types"], ["different", "pilocytic astrocytoma"])
        self.assertEqual(response_json["cancer_types_count"], 2)
        self.assertEqual(response_json["labs_count"], 2)
        self.assertEqual(response_json["projects_count"], 3)
        self.assertEqual(response_json["samples_count"], 4)
