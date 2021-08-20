from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from faker import Faker

from scpca_portal.test.factories import ComputedFileFactory

fake = Faker()


class ComputedFilesTestCase(APITestCase):
    """
    Tests /computed_files/ operations.
    """

    def setUp(self):
        self.computed_file = ComputedFileFactory()

    def test_get_single(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get(reverse("computed-files-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # One for self.computed_file, and one for
        # self.computed_file.sample.project.computed_file
        self.assertEqual(response.json()["count"], 2)

    def test_post_is_not_allowed(self):
        url = reverse("computed-files-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("computed-files-detail", args=[self.computed_file.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
