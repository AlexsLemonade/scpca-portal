from datetime import datetime, timedelta

# from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from scpca_portal.enums import JobStates
from scpca_portal.job_processors import DatasetJobProcessor
from scpca_portal.test.factories import CCDLDatasetFactory, JobFactory, UserDatasetFactory


class TestDatasetJobProcessor(TestCase):

    def test_on_run_done_expires_at_for_user_dataset(self):
        succeeded_at = make_aware(datetime.now())

        job = JobFactory(
            state=JobStates.SUCCEEDED, dataset=UserDatasetFactory(succeeded_at=succeeded_at)
        )
        processor = DatasetJobProcessor(job)
        processor.on_run_done()

        expected_value = succeeded_at + timedelta(days=7)
        self.assertEqual(job.dataset.expires_at, expected_value)

    def test_on_run_done_no_expires_at_for_ccdl_dataset(self):
        succeeded_at = make_aware(datetime.now())

        job = JobFactory(
            state=JobStates.SUCCEEDED, dataset=CCDLDatasetFactory(succeeded_at=succeeded_at)
        )
        processor = DatasetJobProcessor(job)
        processor.on_run_done()

        expected_value = None
        self.assertIsNone(job.dataset.expires_at, expected_value)
