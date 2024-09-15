from functools import partial
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import common
from scpca_portal.models import Project


class TestLoadData(TestCase):
    def setUp(self):
        self.load_data = partial(call_command, "load_data")
        # Bind default values to test object for easy access
        self.input_bucket_name = settings.AWS_S3_INPUT_BUCKET_NAME
        self.clean_up_input_data = False
        self.clean_up_output_data = False
        self.max_workers = 10
        self.reload_existing = False
        self.scpca_project_id = None
        self.update_s3 = False
        self.submitter_whitelist = common.SUBMITTER_WHITELIST

    @patch("scpca_portal.loader.remove_project_input_files")
    @patch("scpca_portal.loader.generate_computed_files")
    @patch("scpca_portal.loader.create_project")
    @patch("scpca_portal.loader.get_projects_metadata")
    def test_input_bucket_name(
        self,
        mock_get_projects_metadata,
        mock_create_project,
        mock_generate_computed_files,
        mock_remove_project_input_files,
    ):
        projects_metadata = [{"key": "value"}]
        mock_get_projects_metadata.return_value = projects_metadata
        mock_create_project.return_value = Project()

        input_bucket_name = "input_bucket_name"
        self.load_data(
            input_bucket_name=input_bucket_name,
            clean_up_input_data=True,
        )

        mock_get_projects_metadata.assert_called_once_with(input_bucket_name, self.scpca_project_id)
        mock_create_project.assert_called_once_with(
            projects_metadata[0],
            self.submitter_whitelist,
            input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )
        mock_generate_computed_files.assert_called_once()
        mock_remove_project_input_files.assert_called_once()

    def test_clean_up_input_data(self):
        pass

    def test_clean_up_output_data(self):
        pass

    def test_reload_existing(self):
        pass

    def test_scpca_project_id_passed(self):
        pass

    def test_no_scpca_project_id_passed(self):
        pass

    def test_update_s3(self):
        pass

    def test_submitter_whitelist(self):
        pass
