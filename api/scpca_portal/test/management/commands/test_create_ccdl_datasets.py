from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.models import Dataset, Job


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

    @patch("scpca_portal.batch.submit_job")
    def test_ignore_hash(self, mock_batch_submit_job):
        mock_batch_job_id = "MOCK_JOB_ID"
        mock_batch_submit_job.return_value = mock_batch_job_id

        # There are 21 total datasets created (with one job per created dataset)
        #     CCDL DATASET TYPE              Total   Projects   Portal Wide
        #   - ALL_METADATA                   4       3          Yes
        #   - SINGLE_CELL_SCE                4       3          Yes
        #   - SINGLE_CELL_SCE_NO_MULTIPLEXED 1       1          No
        #   - SINGLE_CELL_SCE_MERGED         3       2          Yes
        #   - SINGLE_CELL_ANN_DATA           4       3          Yes
        #   - SINGLE_CELL_ANN_DATA_MERGED    3       2          Yes
        #   - SPATIAL_SCE                    2       1          Yes
        call_command("create_ccdl_datasets")
        self.assertEqual(Dataset.objects.count(), 21)
        self.assertEqual(Job.objects.count(), 21)

        # call command again to assert that no new jobs have been created
        call_command("create_ccdl_datasets")
        self.assertEqual(Dataset.objects.count(), 21)
        self.assertEqual(Job.objects.count(), 21)

        # call command again with ignore_hash which should create new jobs
        call_command("create_ccdl_datasets", ignore_hash=True)
        self.assertEqual(Dataset.objects.count(), 21)
        self.assertEqual(Job.objects.count(), 42)
