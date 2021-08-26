from unittest.mock import patch

from django.test import TestCase

from scpca_portal.management.commands.load_data import load_data_from_s3
from scpca_portal.management.commands.purge_project import purge_project
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample


class DataLoadingTestCase(TestCase):
    def test_load_data_from_s3_no_upload(self):
        load_data_from_s3(False, False, "scpca-portal-public-test-inputs", "/home/user/test_data/")

        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.get(pi_name="dyer_chen")
        self.assertNotNone(project.title)
        self.assertNotNone(project.abstract)
        self.assertNotNone(project.contact)
        self.assertNotNone(project.disease)
        self.assertNotNone(project.diagnoses)
        self.assertNotNone(project.seq_units)
        self.assertNotNone(project.technologies)
        self.assertEqual(project.sample_count, 1)
        self.assertEqual(project.summaries.count(), 1)

        self.assertEqual(ProjectSummary.objects.count(), 1)
        project_summary = project.summaries.first()
        self.assertNotNone(project_summary.diagnosis)
        self.assertNotNone(project_summary.seq_unit)
        self.assertNotNone(project_summary.technology)
        self.assertEqual(project_summary.sample_count, 1)

        self.assertEqual(Sample.objects.count(), 1)
        sample = project.samples.first()
        self.assertNotNone(sample.has_cite_seq_data)
        self.assertNotNone(sample.scpca_sample_id)
        self.assertNotNone(sample.technologies)
        self.assertNotNone(sample.diagnosis)
        self.assertNotNone(sample.subdiagnosis)
        self.assertNotNone(sample.age_at_diagnosis)
        self.assertNotNone(sample.sex)
        self.assertNotNone(sample.disease_timing)
        self.assertNotNone(sample.tissue_location)
        self.assertNotNone(sample.treatment)
        self.assertNotNone(sample.seq_units)
        self.assertEqual(len(sample.additional_metadata.keys()), 4)

        # None of ComputedFile's fields can be None, so no need for
        # any checks other than that they exist.
        self.assertNotNone(project.computed_file)
        self.assertNotNone(sample.computed_file)

    # Patch s3.upload_file, which is a tad tricky
    # @patch("data_refinery_foreman.surveyor.external_source.send_job")
    # def test_load_data_from_s3_with_upload(self, mock_send_task):
    #     pass
