from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.test.factories import ProjectFactory


class TestLoadData(TestCase):
    def setUp(self):
        self.dispatch_to_batch = partial(call_command, "dispatch_to_batch")

    @patch("scpca_portal.management.commands.dispatch_to_batch.Command.submit_job")
    def test_only_projects_without_computed_files_submitted(self, mock_submit_job):
        project_with_files = ProjectFactory()

        project_no_files = ProjectFactory()
        project_no_files.computed_files.delete()

        # TODO: remove this patch when we get rid of sample computed file generation
        with patch("scpca_portal.models.Project.samples_to_generate", []):
            self.dispatch_to_batch()
        mock_submit_job.assert_called()

        submitted_project_ids = set(
            call.kwargs["project_id"] for call in mock_submit_job.call_args_list
        )
        self.assertIn(project_no_files.scpca_id, submitted_project_ids)
        self.assertNotIn(project_with_files.scpca_id, submitted_project_ids)
