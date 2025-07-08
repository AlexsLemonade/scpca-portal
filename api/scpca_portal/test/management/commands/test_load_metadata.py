from functools import partial
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import common, metadata_parser
from scpca_portal.models import Project
from scpca_portal.test.factories import OriginalFileFactory


class TestLoadMetadata(TestCase):
    def setUp(self):
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
        prep_data_dirs_patch = patch("scpca_portal.utils.prep_data_dirs")
        get_lockfile_project_ids = patch("scpca_portal.lockfile.get_lockfile_project_ids")
        get_projects_metadata_patch = patch("scpca_portal.loader.get_projects_metadata")
        create_project_patch = patch("scpca_portal.loader.create_project")
        remove_project_input_files_patch = patch("scpca_portal.utils.remove_project_input_files")

        # Start patches
        self.mock_prep_data_dirs = prep_data_dirs_patch.start()
        self.mock_get_lockfile_project_ids = get_lockfile_project_ids.start()
        self.mock_get_projects_metadata = get_projects_metadata_patch.start()
        self.mock_create_project = create_project_patch.start()
        self.mock_remove_project_input_files = remove_project_input_files_patch.start()

        # Save patches that so they can be stopped during tearDown
        self.patches = [
            prep_data_dirs_patch,
            get_lockfile_project_ids,
            get_projects_metadata_patch,
            create_project_patch,
            remove_project_input_files_patch,
        ]

        # Configure necessary output values
        self.mock_get_lockfile_project_ids.return_value = []
        self.projects_metadata = [{"key": "value"}]
        self.mock_get_projects_metadata.return_value = self.projects_metadata
        self.project = Project()
        self.mock_create_project.return_value = self.project

        # Populate OriginalFile to prevent exception when calling load_metadata
        OriginalFileFactory()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def assertMethodsCalled(self):
        self.mock_prep_data_dirs.assert_called()
        self.mock_get_projects_metadata.assert_called()
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
        self.mock_remove_project_input_files.assert_not_called()

        clean_up_input_data = True
        self.load_metadata(clean_up_input_data=clean_up_input_data)
        self.mock_remove_project_input_files.assert_called_once()

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
        scpca_project_id = metadata_parser.get_projects_metadata_ids()[0]
        project = Project(scpca_id=scpca_project_id)
        project.save()

        self.load_metadata(scpca_project_id=scpca_project_id)
        self.mock_get_projects_metadata.assert_called_with(filter_on_project_ids=[scpca_project_id])

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

    def test_get_projects_metadata_failure(self):
        self.mock_get_projects_metadata.return_value = []
        self.load_metadata()

        self.mock_prep_data_dirs.assert_called_once()
        self.mock_get_projects_metadata.assert_called_once()
        self.mock_create_project.assert_not_called()
        self.mock_remove_project_input_files.assert_not_called()

    def test_create_project_failure(self):
        self.mock_create_project.return_value = None
        self.load_metadata()

        self.mock_prep_data_dirs.assert_called_once()
        self.mock_get_projects_metadata.assert_called_once()
        self.mock_create_project.assert_called_once()
        self.mock_remove_project_input_files.assert_not_called()
