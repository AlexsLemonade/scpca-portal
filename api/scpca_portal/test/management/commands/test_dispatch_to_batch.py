from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.test.factories import ProjectFactory


class TestDispatchToBatch(TestCase):
    def setUp(self):
        self.dispatch_to_batch = partial(call_command, "dispatch_to_batch")

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_generate_all_missing_files(self, mock_submit_job):
        project_with_files = ProjectFactory()
        project_no_files = ProjectFactory(computed_file=None)

        self.dispatch_to_batch()
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id") for call in mock_submit_job.call_args_list
        )
        self.assertIn(project_no_files.scpca_id, submitted_project_ids)
        self.assertNotIn(project_with_files.scpca_id, submitted_project_ids)

        sample_no_files = project_no_files.samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id") for call in mock_submit_job.call_args_list
        )
        self.assertIn(sample_no_files.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_generate_missing_files_for_passed_project(self, mock_submit_job):
        project = ProjectFactory(computed_file=None)

        self.dispatch_to_batch(project_id=project.scpca_id)
        mock_submit_job.assert_called()

        submitted_project_id = next(
            call.kwargs["project_id"]
            for call in mock_submit_job.call_args_list
            if "project_id" in call.kwargs
        )
        self.assertEqual(project.scpca_id, submitted_project_id)

        sample = project.samples.first()
        submitted_sample_id = next(
            call.kwargs["sample_id"]
            for call in mock_submit_job.call_args_list
            if "sample_id" in call.kwargs
        )
        self.assertEqual(sample.scpca_id, submitted_sample_id)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_regenerate_all_files(self, mock_submit_job):
        project_with_files = ProjectFactory()
        project_no_files = ProjectFactory(computed_file=None)

        self.dispatch_to_batch(regenerate_all=True)
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id") for call in mock_submit_job.call_args_list
        )
        self.assertIn(project_no_files.scpca_id, submitted_project_ids)
        self.assertIn(project_with_files.scpca_id, submitted_project_ids)

        sample_no_files = project_no_files.samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id") for call in mock_submit_job.call_args_list
        )
        self.assertIn(sample_no_files.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_regenerate_files_for_passed_project(self, mock_submit_job):
        project = ProjectFactory()

        self.dispatch_to_batch(project_id=project.scpca_id, regenerate_all=True)
        mock_submit_job.assert_called()

        submitted_project_id = next(
            call.kwargs["project_id"]
            for call in mock_submit_job.call_args_list
            if "project_id" in call.kwargs
        )
        self.assertEqual(project.scpca_id, submitted_project_id)

        sample = project.samples.first()
        submitted_sample_id = next(
            call.kwargs["sample_id"]
            for call in mock_submit_job.call_args_list
            if "sample_id" in call.kwargs
        )
        self.assertEqual(sample.scpca_id, submitted_sample_id)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_no_missing_computed_files(self, mock_submit_job):
        ProjectFactory()

        self.dispatch_to_batch()
        mock_submit_job.assert_not_called()

    def test_project_missing_samples(self):
        """
        We currently don't support generation of individual samples.
        We plan on removing sample file generation in favor of Dataset downloads.
        """
        pass
