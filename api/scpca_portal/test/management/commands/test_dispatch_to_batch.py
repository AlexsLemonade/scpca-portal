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
        projects_with_files = [ProjectFactory() for _ in range(3)]
        for project_with_files in projects_with_files:
            self.assertTrue(project_with_files.computed_files.exists())

        projects_no_files = [ProjectFactory(computed_file=None) for _ in range(2)]
        for project_no_files in projects_no_files:
            self.assertFalse(project_no_files.computed_files.exists())

        self.dispatch_to_batch()
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("project_id") is not None
        )
        self.assertEqual(len(projects_no_files), len(submitted_project_ids))
        for project_no_files in projects_no_files:
            self.assertIn(project_no_files.scpca_id, submitted_project_ids)
        for project_with_files in projects_with_files:
            self.assertNotIn(project_with_files.scpca_id, submitted_project_ids)

        sample_no_files = projects_no_files[0].samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("sample_id") is not None
        )
        self.assertIn(sample_no_files.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_generate_missing_files_for_passed_project(self, mock_submit_job):
        project = ProjectFactory(computed_file=None)
        self.assertFalse(project.computed_files.exists())
        adtl_projects = [ProjectFactory(computed_file=None) for _ in range(3)]

        self.dispatch_to_batch(project_id=project.scpca_id)
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("project_id") is not None
        )
        self.assertEqual(len(submitted_project_ids), 1)
        self.assertIn(project.scpca_id, submitted_project_ids)
        for adtl_project in adtl_projects:
            self.assertNotIn(adtl_project.scpca_id, submitted_project_ids)

        sample = project.samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("sample_id") is not None
        )
        self.assertEqual(len(submitted_sample_ids), 1)
        self.assertIn(sample.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_regenerate_all_files(self, mock_submit_job):
        projects_with_files = [ProjectFactory() for _ in range(3)]
        for project_with_files in projects_with_files:
            self.assertTrue(project_with_files.computed_files.exists())

        projects_no_files = [ProjectFactory(computed_file=None) for _ in range(2)]
        for project_no_files in projects_no_files:
            self.assertFalse(project_no_files.computed_files.exists())

        projects = projects_with_files + projects_no_files

        self.dispatch_to_batch(regenerate_all=True)
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("project_id") is not None
        )
        self.assertEqual(len(projects), len(submitted_project_ids))
        for project in projects:
            self.assertIn(project.scpca_id, submitted_project_ids)

        sample_no_files = projects[0].samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("sample_id") is not None
        )
        self.assertIn(sample_no_files.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_regenerate_files_for_passed_project(self, mock_submit_job):
        project = ProjectFactory()
        self.assertTrue(project.computed_files.exists())
        adtl_projects = [ProjectFactory() for _ in range(3)]
        for adtl_project in adtl_projects:
            self.assertTrue(adtl_project.computed_files.exists())

        self.dispatch_to_batch(project_id=project.scpca_id, regenerate_all=True)
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs.get("project_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("project_id") is not None
        )
        self.assertEqual(len(submitted_project_ids), 1)
        self.assertIn(project.scpca_id, submitted_project_ids)
        for adtl_project in adtl_projects:
            self.assertNotIn(adtl_project.scpca_id, submitted_project_ids)

        sample = project.samples.first()
        submitted_sample_ids = set(
            call.kwargs.get("sample_id")
            for call in mock_submit_job.call_args_list
            if call.kwargs.get("sample_id") is not None
        )
        self.assertEqual(len(submitted_sample_ids), 1)
        self.assertIn(sample.scpca_id, submitted_sample_ids)

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_no_missing_computed_files(self, mock_submit_job):
        project = ProjectFactory()
        self.assertTrue(project.computed_files.exists())

        self.dispatch_to_batch()
        mock_submit_job.assert_not_called()

    def test_project_missing_sample_computed_files(self):
        """
        We currently don't support generation of individual samples.
        We plan on removing sample file generation in favor of Dataset downloads.
        """
        pass
