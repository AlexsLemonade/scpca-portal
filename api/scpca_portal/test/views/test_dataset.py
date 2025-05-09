from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.models import Dataset
from scpca_portal.test.expected_values import DatasetCustomSingleCellExperiment
from scpca_portal.test.factories import DatasetFactory, LeafComputedFileFactory


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    def setUp(self):
        self.ccdl_dataset = DatasetFactory(is_ccdl=True)
        self.custom_dataset = DatasetFactory(is_ccdl=False)
        self.custom_dataset.computed_file = LeafComputedFileFactory()
        self.custom_dataset.save()

    def test_get_single(self):
        url = reverse("datasets-detail", args=[self.ccdl_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), str(self.ccdl_dataset.id))

        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), str(self.custom_dataset.id))
        # Assert that computed_file attribute is a dict an not just the pk
        self.assertIsInstance(response.json().get("computed_file"), dict)

    def test_get_list(self):
        url = reverse("datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(response.json()["count"], 1)
        # Assert that only CCDL datasets are listable
        self.assertNotEqual(response_json["results"][0].get("id"), str(self.custom_dataset.id))
        self.assertEqual(response_json["results"][0].get("id"), str(self.ccdl_dataset.id))

    def test_post(self):
        url = reverse("datasets-list", args=[])
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test adding ccdl datasets doesn't work
        data = {
            "is_ccdl": True,  # this non serialized field should be ignored by DRF
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_dataset = Dataset.objects.filter(id=response.json().get("id")).first()
        self.assertFalse(created_dataset.is_ccdl)

    def test_put(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check to see that read_only format field was not mutated
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": "format",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.custom_dataset.format, data.get("format"))

    def test_delete_is_not_allowed(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("scpca_portal.models.Job.submit")
    def test_create_submit_job(self, mock_submit_job):
        url = reverse("datasets-list", args=[])

        # Test job not started
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
            "start": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_not_called()

        # Test job started
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
            "start": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_called_once()

        # Assert that start attribute was reset to False after kicking off job
        created_dataset_id = response.json().get("id")
        created_dataset = Dataset.objects.filter(id=created_dataset_id).first()
        self.assertFalse(created_dataset.start)
