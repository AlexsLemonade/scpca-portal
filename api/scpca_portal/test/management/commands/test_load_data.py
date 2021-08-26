from unittest.mock import patch

from django.test import TestCase

from scpca_portal.management.commands.load_data import load_data_from_s3
from scpca_portal.management.commands.purge_project import purge_project
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample


class MockS3Client:
    def __init__(self, *args, **kwargs):
        pass

    def upload_file(self, path, bucket, key):
        print(f"Did not upload {path} to {bucket}/{key} because this is a test.")
        pass


class LoadDataTestCase(TestCase):
    def assert_project(self, pi_name, upload_data):
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.get(pi_name=pi_name)

        self.assertIsNotNone(project.title)
        self.assertIsNotNone(project.abstract)
        self.assertIsNotNone(project.contact)
        self.assertIsNotNone(project.disease_timings)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.seq_units)
        self.assertIsNotNone(project.technologies)
        self.assertEqual(project.sample_count, 1)
        self.assertEqual(project.summaries.count(), 1)

        self.assertEqual(ProjectSummary.objects.count(), 1)
        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)
        self.assertEqual(project_summary.sample_count, 1)

        self.assertEqual(Sample.objects.count(), 1)
        sample = project.samples.first()
        self.assertIsNotNone(sample.has_cite_seq_data)
        self.assertIsNotNone(sample.scpca_sample_id)
        self.assertIsNotNone(sample.technologies)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.age_at_diagnosis)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.disease_timing)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.treatment)
        self.assertIsNotNone(sample.seq_units)
        expected_keys = {"COG Risk", "IGSS Stage", "Primary Site", "Treatment"}
        self.assertEqual(set(sample.additional_metadata.keys()), expected_keys)

        self.assertEqual(ComputedFile.objects.count(), 2)
        project_computed_file = project.computed_file
        self.assertIsNotNone(project_computed_file)
        sample_computed_file = sample.computed_file
        self.assertIsNotNone(sample_computed_file)

        if upload_data:
            # The test files are empty, and this was recorded because
            # upload_data was true.
            self.assertEqual(project_computed_file.size_in_bytes, 0)
            self.assertEqual(sample_computed_file.size_in_bytes, 0)
        else:
            # These will have checked the bucket for local dev to get
            # the size of the files it contains.
            self.assertGreater(project_computed_file.size_in_bytes, 0)
            self.assertGreater(sample_computed_file.size_in_bytes, 0)

        return project, project_computed_file, project_summary, sample, sample_computed_file

    def test_load_data_from_s3_no_upload(self):
        pi_name = "dyer_chen"
        upload_data = False
        # First, just test that loading data works.
        load_data_from_s3(
            upload_data, False, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )

        (
            project,
            project_computed_file,
            project_summary,
            sample,
            sample_computed_file,
        ) = self.assert_project(pi_name, upload_data)

        # Next, let's make sure that new_only=True won't add anything
        # new when there's nothing new.
        load_data_from_s3(
            False, True, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(ProjectSummary.objects.count(), 1)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(ComputedFile.objects.count(), 2)

        # project, project_computed_file, project_summary, sample, and
        # sample_computed_file all still reference the what was loaded
        # in the first call.
        new_project = Project.objects.get(pi_name="dyer_chen")
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())
        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)
        self.assertEqual(project_computed_file, new_project.computed_file)
        self.assertEqual(sample_computed_file, new_sample.computed_file)

        # Next, this is a good place to test he purge command since we
        # have data to purge.
        purge_project(pi_name)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Finally, let's make sure that loading, purging, and then
        # reloading works smoothly.
        load_data_from_s3(
            False, True, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(ProjectSummary.objects.count(), 1)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(ComputedFile.objects.count(), 2)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_load_data_from_s3_with_upload(self):
        # mock_boto3.client.return_value = MockS3Client()
        pi_name = "dyer_chen"
        upload_data = True
        # First, just test that loading data works.
        load_data_from_s3(
            upload_data, False, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )

        self.assert_project(pi_name, upload_data)
