from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import LeafProjectFactory, ProjectFactory, SampleFactory


class FilterOptionsTestCase(APITestCase):
    """Tests /project-options/ endpoint."""

    def setUp(self):
        SampleFactory(
            diagnosis="different",
            project=ProjectFactory(),
            seq_units="cell, bulk",
            technologies="10Xv4, 10Xv5",
        )

        # Create a project with no samples.
        LeafProjectFactory()

    def test_get(self):
        url = reverse("project-options-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = response.json()
        self.assertEqual(len(response["diagnoses"]), 4)
        self.assertEqual(len(response["modalities"]), 1)  # CITE-seq only.
        self.assertEqual(len(response["seq_units"]), 2)
        self.assertEqual(len(response["technologies"]), 5)
