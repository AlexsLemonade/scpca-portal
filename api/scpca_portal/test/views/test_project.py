from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.test.factories import ProjectFactory, SampleComputedFileFactory


class ProjectsTestCase(APITestCase):
    """Tests /projects/ operations."""

    def setUp(self):
        self.project = ProjectFactory()

    def test_get_single(self):
        # computed_file = SampleComputedFileFactory()
        # computed_file.prjct = self.project
        # computed_file.save()

        url = reverse("projects-detail", args=[self.project.scpca_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["modalities"], "CITE-seq")
        self.assertEqual(response_json["computed_file"]["size_in_bytes"], 100)

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
