from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ProjectFactory

fake = Faker()


class ProjectsTestCase(APITestCase):
    """
    Tests /projects/ operations.
    """

    def setUp(self):
        self.project = ProjectFactory()

    def test_get_single(self):
        url = reverse("projects-detail", args=[self.project.pi_name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["modalities"], "CITE-seq, Bulk RNA-seq")

    def test_get_list(self):
        response = self.client.get(reverse("projects-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_post_is_not_allowed(self):
        url = reverse("projects-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("projects-detail", args=[self.project.pi_name])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("projects-detail", args=[self.project.pi_name])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
