from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader
from scpca_portal.models import Dataset, Job


class TestCreateCCDLDatasets(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        for project_metadata in loader.get_projects_metadata():
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
                reload_existing=True,
                update_s3=False,
            )

    @patch("scpca_portal.batch.submit_job")
    def test_correct_datasets_and_jobs_processed(self, mock_batch_submit_job):
        mock_batch_job_id = "MOCK_JOB_ID"
        mock_batch_submit_job.return_value = mock_batch_job_id

        call_command("create_ccdl_datasets")
        self.assertEqual(Dataset.objects.count(), 21)
        self.assertEqual(Job.objects.count(), 21)

        # call command again to assert that no new datasets or jobs have been created
        call_command("create_ccdl_datasets")
        self.assertEqual(Dataset.objects.count(), 21)
        self.assertEqual(Job.objects.count(), 21)
