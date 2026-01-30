from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scpca_portal.enums import CCDLDatasetNames, DatasetFormats
from scpca_portal.models import CCDLDataset
from scpca_portal.test.factories import APITokenFactory, CCDLDatasetFactory, UserDatasetFactory


class CCDLDatasetsTestCase(APITestCase):
    """Tests /ccdl-datasets/ operations."""

    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    def test_get_list(self):
        ccdl_dataset = CCDLDatasetFactory()
        user_dataset = UserDatasetFactory()

        url = reverse("ccdl-datasets-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

        # Assert that only CCDL datasets are listable
        response_json = response.json()
        self.assertNotEqual(response_json["results"][0].get("id"), str(user_dataset.id))
        self.assertEqual(response_json["results"][0].get("id"), str(ccdl_dataset.id))

    def test_get_list_with_query_params(self):
        url = reverse("ccdl-datasets-list")

        project_id = "SCPCP999990"
        dataset_project_ann_data = CCDLDatasetFactory(
            ccdl_name=CCDLDatasetNames.SINGLE_CELL_ANN_DATA,
            ccdl_project_id=project_id,
            format=DatasetFormats.ANN_DATA,
        )
        dataset_project_sce = CCDLDatasetFactory(
            ccdl_name=CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT,
            ccdl_project_id=project_id,
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
        )
        dataset_project_metadata = CCDLDatasetFactory(
            ccdl_name=CCDLDatasetNames.ALL_METADATA,
            ccdl_project_id=project_id,
            format=DatasetFormats.METADATA,
        )

        ccdl_project_modality_datasets = [
            dataset_project_ann_data,
            dataset_project_sce,
            dataset_project_metadata,
        ]

        # Assert filtering with a query param
        response = self.client.get(url, {"ccdl_project_id": project_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["count"], 3)

        expected_dataset_ids = {str(dataset.id) for dataset in ccdl_project_modality_datasets}
        actual_dataset_ids = {result["id"] for result in response_json["results"]}
        self.assertEqual(actual_dataset_ids, expected_dataset_ids)

        # Assert filtering with multiple query params
        response = self.client.get(
            url, {"ccdl_project_id": project_id, "format": "SINGLE_CELL_EXPERIMENT"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["count"], 1)
        self.assertNotEqual(response_json["results"][0].get("id"), str(dataset_project_sce))

    def test_get_single_no_token(self):
        ccdl_dataset = CCDLDatasetFactory()
        user_dataset = UserDatasetFactory()

        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), str(ccdl_dataset.id))

        # download_url is only made available when a valid token is passed
        self.assertNotIn("download_url", response.json())

        # Assert non existing dataset adequately 404s
        dataset = CCDLDataset(data={})
        url = reverse("ccdl-datasets-detail", args=[dataset.id])
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert custom dataset 404s
        url = reverse("ccdl-datasets-detail", args=[user_dataset.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "scpca_portal.models.datasets.ccdl_dataset.CCDLDataset.download_url",
        new_callable=PropertyMock,
        return_value="file.zip",
    )
    def test_get_single_with_valid_token(self, _):
        ccdl_dataset = CCDLDatasetFactory()
        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])

        token = APITokenFactory()
        response = self.client.get(url, HTTP_API_KEY=token.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone("download_url", response.json())

    def test_get_single_with_bad_token(self):
        ccdl_dataset = CCDLDatasetFactory()
        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])

        # invalid token
        response = self.client.get(url, HTTP_API_KEY="invalid token")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # inactive token
        token = APITokenFactory(is_activated=False)
        response = self.client.get(url, HTTP_API_KEY=token.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_is_not_allowed(self):
        url = reverse("ccdl-datasets-list", args=[])
        response = self.client.post(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        ccdl_dataset = CCDLDatasetFactory()
        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])
        response = self.client.put(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        ccdl_dataset = CCDLDatasetFactory()
        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])
        response = self.client.patch(url, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        ccdl_dataset = CCDLDatasetFactory()
        url = reverse("ccdl-datasets-detail", args=[ccdl_dataset.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
