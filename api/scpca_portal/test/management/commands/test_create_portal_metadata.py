import shutil

from django.test import TransactionTestCase

from scpca_portal import common
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import Project

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.

ALLOWED_SUBMITTERS = {"scpca"}


class TestCreatePortalMetadata(TransactionTestCase):
    def setUp(self):
        self.processor = create_portal_metadata.Command()
        self.loader = load_data.Command()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def setup_database(self, project_ids):
        for project_id in project_ids:
            self.loader.load_data(
                allowed_submitters=list(ALLOWED_SUBMITTERS),
                clean_up_input_data=False,
                clean_up_output_data=False,
                max_workers=4,
                reload_all=False,
                reload_existing=False,
                scpca_project_id=project_id,
                update_s3=False,
            )

    def test_create_portal_metadata(self):
        # Set up the database
        project_ids = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]
        self.setup_database(project_ids)

        # Make sure that the number of projects created matches the length of project_ids
        self.assertEqual(Project.objects.count(), len(project_ids))

        # Once the database is set up correctly, run the create_portal_metadata management command
        self.processor.create_portal_metadata(clean_up_output_data=False)

        # Test the content of the generated zip file here
