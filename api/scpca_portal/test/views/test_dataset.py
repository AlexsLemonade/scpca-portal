from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.enums import DatasetFormats
from scpca_portal.models import UserDataset
from scpca_portal.test.expected_values import UserDatasetSingleCellExperiment
from scpca_portal.test.factories import (
    APITokenFactory,
    CCDLDatasetFactory,
    LeafComputedFileFactory,
    ProjectFactory,
    SampleFactory,
    UserDatasetFactory,
)


class DatasetsTestCase(APITestCase):
    """Tests /datasets/ operations."""

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        # create user dataset project and samples objects
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
        user_dataset = UserDatasetFactory(computed_file=LeafComputedFileFactory())
        ccdl_dataset = CCDLDatasetFactory()

        url = reverse("datasets-detail", args=[user_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), str(user_dataset.id))

        # download_url is only made available when a valid token is passed
        self.assertNotIn("download_url", response.json())

        # Assert that computed_file attribute is a dict an not just the pk
        self.assertIsInstance(response.json().get("computed_file"), dict)

        # Assert that only user datasets are retrievable
        url = reverse("datasets-detail", args=[ccdl_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert non existing dataset adequately 404s
        dataset = UserDataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "scpca_portal.models.datasets.user_dataset.UserDataset.download_url",
        new_callable=PropertyMock,
        return_value="file.zip",
    )
    def test_get_single_with_valid_token(self, _):
        user_dataset = UserDatasetFactory()
        url = reverse("datasets-detail", args=[user_dataset.id])

        token = APITokenFactory()
        response = self.client.get(url, HTTP_API_KEY=token.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone("download_url", response.json())

    def test_get_single_with_bad_token(self):
        user_dataset = UserDatasetFactory()
        url = reverse("datasets-detail", args=[user_dataset.id])

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
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
            "format": UserDatasetSingleCellExperiment.VALUES.get("format"),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that format must be present
        data = {
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put(self):
        user_dataset = UserDatasetFactory()
        url = reverse("datasets-detail", args=[user_dataset.id])

        user_dataset.format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        user_dataset.save()

        # Assert that format remains unchanged when not present
        data = {
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(user_dataset.format, data.get("format"))

        # Assert that processing dataset cannot be modified
        user_dataset.start = True
        user_dataset.save()
        data = {
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
            "format": DatasetFormats.ANN_DATA,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert non existing dataset adequately 404s
        dataset = UserDataset(data={})
        url = reverse("datasets-detail", args=[dataset.id])
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_format(self):
        user_dataset = UserDatasetFactory()
        url = reverse("datasets-detail", args=[user_dataset.id])
        user_dataset.data = UserDatasetSingleCellExperiment.VALUES.get("data")
        user_dataset.format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        user_dataset.save()

        # Assert that format cannot be modified if dataset already contains data
        data = {"format": DatasetFormats.ANN_DATA}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that format can be modified if dataset is empty
        user_dataset.data = {}
        user_dataset.save()

        data = {"format": DatasetFormats.ANN_DATA}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_is_not_allowed(self):
        url = reverse("datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        user_dataset = UserDatasetFactory()
        url = reverse("datasets-detail", args=[user_dataset.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("scpca_portal.models.Job.submit")
    def test_create_submit_job(self, mock_submit_job):
        url = reverse("datasets-list", args=[])

        # Assert job not started
        data = {
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
            "format": UserDatasetSingleCellExperiment.VALUES.get("format"),
            "start": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_not_called()

        # Assert job started
        data = {
            "data": UserDatasetSingleCellExperiment.VALUES.get("data"),
            "email": UserDatasetSingleCellExperiment.VALUES.get("email"),
            "format": UserDatasetSingleCellExperiment.VALUES.get("format"),
            "start": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit_job.assert_called_once()

    @patch("scpca_portal.models.Job.submit")
    def test_update_submit_job(self, mock_submit_job):
        # Assert that job cannot be started when it's already processing
        dataset = UserDataset(
            data=UserDatasetSingleCellExperiment.VALUES.get("data"),
            email=UserDatasetSingleCellExperiment.VALUES.get("email"),
            format=UserDatasetSingleCellExperiment.VALUES.get("format"),
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
        dataset = UserDataset(
            data=UserDatasetSingleCellExperiment.VALUES.get("data"),
            email=UserDatasetSingleCellExperiment.VALUES.get("email"),
            format=UserDatasetSingleCellExperiment.VALUES.get("format"),
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
