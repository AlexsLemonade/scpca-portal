from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import DatasetFactory, ProjectFactory
from scpca_portal.enums.dataset_formats import DatasetFormats


class ProjectsTestCase(APITestCase):
    """Tests /projects/ operations."""

    def setUp(self):
        self.project = ProjectFactory()
        self.project.update_project_aggregate_properties()

    def test_get_single(self):
        url = reverse("projects-detail", args=[self.project.scpca_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["modalities"], ["CITE_SEQ"])
        self.assertEqual(response_json["computed_files"][0]["size_in_bytes"], 100)

    def test_get_list(self):
        response = self.client.get(reverse("projects-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_post_is_not_allowed(self):
        url = reverse("projects-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("projects-detail", args=[self.project.scpca_id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("projects-detail", args=[self.project.scpca_id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_datasets_field(self):
        datasets = [
            DatasetFactory(is_ccdl=True, ccdl_project_id=self.project.scpca_id) for _ in range(3)
        ]
        metadata_dataset = datasets[-1]
        metadata_dataset.format = DatasetFormats.METADATA
        metadata_dataset.save()

        # detail view
        url = reverse("projects-detail", args=[self.project.scpca_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response_json["metadata_dataset"]["id"], str(metadata_dataset.id))

        # list view
        url = reverse("projects-list", args=[])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response_json["results"][0]["metadata_dataset"]["id"], str(metadata_dataset.id))
