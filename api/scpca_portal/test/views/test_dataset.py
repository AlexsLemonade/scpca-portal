from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.enums import DatasetFormats
from scpca_portal.models import Dataset
from scpca_portal.test.expected_values import DatasetCustomSingleCellExperiment
from scpca_portal.test.factories import (
    APITokenFactory,
    DatasetFactory,
    LeafComputedFileFactory,
    ProjectFactory,
    SampleFactory,
)


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        cls.ccdl_dataset = DatasetFactory(is_ccdl=True)
        cls.custom_dataset = DatasetFactory(
            is_ccdl=False,
            computed_file=LeafComputedFileFactory(),
        )

        # create custom dataset project and samples objects
        project = ProjectFactory(scpca_id="SCPCP999990", has_bulk_rna_seq=True)
        SampleFactory(scpca_id="SCPCS999990", project=project, has_single_cell_data=True)
        SampleFactory(scpca_id="SCPCS999997", project=project, has_single_cell_data=True)
        SampleFactory(scpca_id="SCPCS999991", project=project, has_spatial_data=True)

        project = ProjectFactory(
            scpca_id="SCPCP999992", has_bulk_rna_seq=True, includes_merged_sce=True
        )
        SampleFactory(scpca_id="SCPCS999996", project=project, has_single_cell_data=True)
        SampleFactory(scpca_id="SCPCS999998", project=project, has_single_cell_data=True)

    def test_get_single_no_token(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), str(self.custom_dataset.id))

        # download_url is only made available when a valid token is passed
        self.assertNotIn("download_url", response.json())

        # Assert that computed_file attribute is a dict an not just the pk
        self.assertIsInstance(response.json().get("computed_file"), dict)

        # Assert that only custom datasets are retrievable
        url = reverse("datasets-detail", args=[self.ccdl_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert non existing dataset adequately 404s
        dataset = Dataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "scpca_portal.models.dataset.Dataset.download_url",
        new_callable=PropertyMock,
        return_value="file.zip",
    )
    def test_get_single_with_valid_token(self, _):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])

        token = APITokenFactory()
        response = self.client.get(url, HTTP_API_KEY=token.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone("download_url", response.json())

    def test_get_single_with_bad_token(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])

        # invalid token
        response = self.client.get(url, HTTP_API_KEY="invalid token")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # inactive token
        token = APITokenFactory(is_activated=False)
        response = self.client.get(url, HTTP_API_KEY=token.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post(self):
        url = reverse("datasets-list", args=[])
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that format must be present
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that adding ccdl datasets doesn't work
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

        self.custom_dataset.format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        self.custom_dataset.save()

        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetFormats.SINGLE_CELL_EXPERIMENT,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that processing dataset cannot be modified
        self.custom_dataset.start = True
        self.custom_dataset.save()
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert non existing dataset adequately 404s
        dataset = Dataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_is_not_allowed(self):
        url = reverse("datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("datasets-detail", args=[self.custom_dataset.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_not_called()

        # Assert job started
        data = {
            "data": DatasetCustomSingleCellExperiment.VALUES.get("data"),
            "email": DatasetCustomSingleCellExperiment.VALUES.get("email"),
            "format": DatasetCustomSingleCellExperiment.VALUES.get("format"),
            "start": True,
        }
        response = self.client.post(url, data)
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
        response = self.client.put(url, data)
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
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_submit_job.assert_called_once()
