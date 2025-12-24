from functools import partial
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import common
from scpca_portal.models import Project
from scpca_portal.test.factories import OriginalFileFactory


class TestLoadMetadata(TestCase):
    def setUp(self):
        with patch(
            "scpca_portal.lockfile.get_locked_project_ids",
            return_value=[],
        ):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)
        self.load_metadata = partial(call_command, "load_metadata")
        # Bind default function params to test object for easy access
        self.input_bucket_name = settings.AWS_S3_INPUT_BUCKET_NAME
        self.clean_up_input_data = False
        self.reload_existing = False
        self.reload_locked = False
        self.scpca_project_id = None
        self.update_s3 = False
        self.submitter_whitelist = common.SUBMITTER_WHITELIST

        # Handle patching in setUp function
        create_data_dirs_patch = patch("scpca_portal.utils.create_data_dirs")
        download_files_patch = patch("scpca_portal.s3.download_files")
        get_projects_metadata_ids_patch = patch(
            "scpca_portal.metadata_parser.get_projects_metadata_ids"
        )
        load_projects_metadata_patch = patch("scpca_portal.metadata_parser.load_projects_metadata")
        create_project_patch = patch("scpca_portal.loader.create_project")
        remove_nested_data_dirs_patch = patch("scpca_portal.utils.remove_nested_data_dirs")

        # Start patches
        self.mock_create_data_dirs = create_data_dirs_patch.start()
        self.mock_download_files_patch = download_files_patch.start()
        self.mock_get_projects_metadata_ids_patch = get_projects_metadata_ids_patch.start()
        self.mock_load_projects_metadata = load_projects_metadata_patch.start()
        self.mock_create_project = create_project_patch.start()
        self.mock_remove_nested_data_dirs = remove_nested_data_dirs_patch.start()

        # Save patches that so they can be stopped during tearDown
        self.patches = [
            create_data_dirs_patch,
            download_files_patch,
            get_projects_metadata_ids_patch,
            load_projects_metadata_patch,
            create_project_patch,
            remove_nested_data_dirs_patch,
        ]

        # Configure necessary output values
        self.projects_metadata = [{"key": "value"}]
        self.mock_get_projects_metadata_ids_patch.return_value = {"SCPCP999990"}
        self.mock_load_projects_metadata.return_value = self.projects_metadata
        self.project = Project()

        # Populate OriginalFile to prevent exception when calling load_metadata
        OriginalFileFactory()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def assertMethodsCalled(self):
        self.mock_create_data_dirs.assert_called()
        self.mock_load_projects_metadata.assert_called()
        self.mock_create_project.assert_called()

    def test_input_bucket_name(self):
        self.load_metadata()
        self.assertMethodsCalled()

        self.mock_create_project.assert_called_once_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

        input_bucket_name = "input_bucket_name"
        self.load_metadata(input_bucket_name=input_bucket_name)

        self.mock_create_project.assert_called_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

    def test_clean_up_input_data(self):
        self.load_metadata()
        self.assertMethodsCalled()
        self.mock_remove_nested_data_dirs.assert_not_called()

        clean_up_input_data = True
        self.load_metadata(clean_up_input_data=clean_up_input_data)
        self.mock_remove_nested_data_dirs.assert_called_once()

    def test_reload_existing(self):
        self.load_metadata()
        self.assertMethodsCalled()
        self.mock_create_project.assert_called_once_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

        reload_existing = True
        self.load_metadata(reload_existing=reload_existing)
        self.mock_create_project.assert_called_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            reload_existing,
            self.update_s3,
        )

    def test_reload_locked(self):
        self.load_metadata()
        self.assertMethodsCalled()
        self.mock_create_project.assert_called_once_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

        reload_locked = True
        self.load_metadata(reload_locked=reload_locked)
        self.mock_create_project.assert_called_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

    def test_scpca_project_id(self):
        scpca_project_id = "SCPCP999990"
        project = Project(scpca_id=scpca_project_id)
        project.save()

        self.load_metadata(scpca_project_id=scpca_project_id)
        self.mock_load_projects_metadata.assert_called_with([scpca_project_id])

    def test_update_s3(self):
        self.load_metadata()
        self.assertMethodsCalled()
        self.mock_create_project.assert_called_once_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

        update_s3 = True
        self.load_metadata(update_s3=update_s3)
        self.mock_create_project.assert_called_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            update_s3,
        )

    def test_submitter_whitelist(self):
        self.load_metadata()
        self.assertMethodsCalled()
        self.mock_create_project.assert_called_once_with(
            self.projects_metadata[0],
            self.submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

        submitter_whitelist = {"submitter"}
        self.load_metadata(submitter_whitelist=submitter_whitelist)
        self.mock_create_project.assert_called_with(
            self.projects_metadata[0],
            submitter_whitelist,
            self.input_bucket_name,
            self.reload_existing,
            self.update_s3,
        )

    def test_load_projects_metadata_failure(self):
        self.mock_load_projects_metadata.return_value = []
        self.load_metadata()

        self.mock_create_data_dirs.assert_called_once()
        self.mock_load_projects_metadata.assert_called_once()
        self.mock_create_project.assert_not_called()
        self.mock_remove_nested_data_dirs.assert_not_called()

    def test_create_project_failure(self):
        self.mock_create_project.return_value = None
        self.load_metadata()

        self.mock_create_data_dirs.assert_called_once()
        self.mock_load_projects_metadata.assert_called_once()
        self.mock_create_project.assert_called_once()
        self.mock_remove_nested_data_dirs.assert_not_called()
