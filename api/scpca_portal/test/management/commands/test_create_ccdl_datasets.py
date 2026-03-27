from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.enums.job_states import JobStates
from scpca_portal.test.factories import JobFactory


class TestCreateCCDLDatasets(TestCase):
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
