from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.models import APIToken, Dataset
from scpca_portal.test.expected_values import DatasetCustomSingleCellExperiment
from scpca_portal.test.factories import DatasetFactory, LeafComputedFileFactory


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    def setUp(self):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        self.token = APIToken(email="user@example.com", is_activated=True)
        self.token.save()

        self.auth_headers = {"HTTP_API_KEY": str(self.token.id)}

        self.ccdl_dataset = DatasetFactory(is_ccdl=True, token=self.token)
        self.custom_dataset = DatasetFactory(
            is_ccdl=False,
            token=self.token,
            computed_file=LeafComputedFileFactory(),
        )

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

        # Assert non existing dataset adequately 404s
        dataset = Dataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list(self):
        url = reverse("datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_json = response.json()
        self.assertEqual(len(response.json()), 1)
        # Assert that only CCDL datasets are listable
        self.assertNotEqual(response_json[0].get("id"), str(self.custom_dataset.id))
        self.assertEqual(response_json[0].get("id"), str(self.ccdl_dataset.id))

    def test_post(self):
        url = reverse("datasets-list", args=[])
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        # Assert failure when token is not passed
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert success when token is passed
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that adding ccdl datasets doesn't work
        data = {
            "is_ccdl": True,  # this non serialized field should be ignored by DRF
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_dataset = Dataset.objects.filter(id=response.json().get("id")).first()
        self.assertFalse(created_dataset.is_ccdl)

    def test_put(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
        }
        # Assert failure when token is not passed
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert success when token is passed
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that read_only format field was not mutated
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": "format",
        }
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.custom_dataset.format, data.get("format"))

        # Assert that processing dataset cannot be modified
        self.custom_dataset.start = True
        self.custom_dataset.save()
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": "format",
        }
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert non existing dataset adequately 404s
        dataset = Dataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.put(url, {}, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_is_not_allowed(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_stats_property_keys(self):
        url = reverse("datasets-detail", args=[self.ccdl_dataset.id])
        response = self.client.get(url)
        stats_property = response.json().get("stats")
        stats_property_fields = {
            "current_data_hash",
            "current_readme_hash",
            "current_metadata_hash",
            "is_hash_changed",
            "uncompressed_size",
        }
        for field in stats_property_fields:
            self.assertIn(field, stats_property)

    @patch("scpca_portal.models.Job.submit")
    def test_create_submit_job(self, mock_submit_job):
        url = reverse("datasets-list", args=[])

        # Assert job not started
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
            "start": False,
        }
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_not_called()

        # Assert job started
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
            "start": True,
        }
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_called_once()

    @patch("scpca_portal.models.Job.submit")
    def test_update_submit_job(self, mock_submit_job):
        # Assert that job cannot be started when it's already processing
        dataset = Dataset(
            data=DatasetCustomSingleCellExperiment.VALUES.get("data"),
            email=DatasetCustomSingleCellExperiment.VALUES.get("email"),
            format=DatasetCustomSingleCellExperiment.VALUES.get("format"),
            start=True,
        )
        dataset.save()
        url = reverse("datasets-detail", args=[dataset.id])
        data = {
            "start": True,
        }
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        mock_submit_job.assert_not_called()

        # Assert that not started job can be started
        dataset = Dataset(
            data=DatasetCustomSingleCellExperiment.VALUES.get("data"),
            email=DatasetCustomSingleCellExperiment.VALUES.get("email"),
            format=DatasetCustomSingleCellExperiment.VALUES.get("format"),
            start=False,
        )
        dataset.save()
        url = reverse("datasets-detail", args=[dataset.id])
        data = {
            "start": True,
        }
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_submit_job.assert_called_once()
