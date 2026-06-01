from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.enums.job_states import JobStates
from scpca_portal.models import CCDLDataset, Job
from scpca_portal.test.factories import JobFactory


class TestCreateCCDLDatasets(TestCase):
    @classmethod
    def setUpTestData(cls):
        bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        call_command("sync_original_files", bucket=bucket)

        loader.download_projects_metadata()
        project_ids = metadata_parser.get_projects_metadata_ids(bucket=bucket)

        loader.download_projects_related_metadata(project_ids)
        for project_metadata in metadata_parser.load_projects_metadata(project_ids):
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=bucket,
                reload_existing=True,
                update_s3=False,
            )

    @patch("scpca_portal.models.Job.submit_ccdl_datasets")
    def test_ignore_hash(self, mock_submit_ccdl_datasets):
        mock_submit_ccdl_datasets.return_value = [], []
        with patch(
            "scpca_portal.models.CCDLDataset.create_or_update_ccdl_datasets", return_value=([], [])
        ) as mock_create_or_update_ccdl_datasets:
            ignore_hash = False
            call_command("create_ccdl_datasets", ignore_hash=ignore_hash)
            mock_create_or_update_ccdl_datasets.assert_called_with(ignore_hash=ignore_hash)

            ignore_hash = True
            call_command("create_ccdl_datasets", ignore_hash=ignore_hash)
            mock_create_or_update_ccdl_datasets.assert_called_with(ignore_hash=ignore_hash)

    @patch("scpca_portal.models.Job.submit_ccdl_datasets")
    @patch("scpca_portal.models.CCDLDataset.create_or_update_ccdl_datasets")
    def test_retry_failed_jobs(
        self, mock_create_or_update_ccdl_datasets, mock_submit_ccdl_datasets
    ):
        failed_jobs = [JobFactory(state=JobStates.FAILED) for _ in range(3)]
        mock_create_or_update_ccdl_datasets.return_value = [], []
        mock_submit_ccdl_datasets.return_value = [], failed_jobs

        # call command to assert that job attempt not increased
        call_command("create_ccdl_datasets", retry_failed_jobs=False)
        for job in failed_jobs:
            self.assertEqual(job.attempt, 1)

        # call command to assert that job attempt increased
        call_command("create_ccdl_datasets", retry_failed_jobs=True)
        for job in failed_jobs:
            self.assertEqual(job.attempt, 2)

    @patch("scpca_portal.models.Job.submit")
    def test_submit_ccdl_datasets(self, mock_submit_job):
        created_datasets, updated_datasets = CCDLDataset.create_or_update_ccdl_datasets()
        self.assertEqual(len(created_datasets), 21)
        self.assertEqual(len(updated_datasets), 0)

        submitted_jobs, failed_jobs = Job.submit_ccdl_datasets(created_datasets + updated_datasets)
        self.assertEqual(len(submitted_jobs), 21)
        self.assertEqual(len(failed_jobs), 0)

        self.assertEqual(mock_submit_job.call_count, 21)
        # Datasets from submitted jobs should be marked as started
        for job in submitted_jobs:
            self.assertTrue(job.dataset.is_started)
            self.assertIsInstance(job.dataset.started_at, datetime)
