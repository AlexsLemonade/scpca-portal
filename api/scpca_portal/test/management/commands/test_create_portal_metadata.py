import shutil

from django.test import TransactionTestCase

from scpca_portal import common
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import Library

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

    def load_test_data(self):
        self.loader.load_data(
            allowed_submitters=list(ALLOWED_SUBMITTERS),
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )

    def test_create_portal_metadata(self):
        # Set up the database
        PROJECT_COUNT = 3
        SAMPLES_COUNT = 8
        LIBRARIES_COUNT = 7

        self.load_test_data()

        libraries = Library.objects.all()
        libraries_metadata = [
            lib for library in libraries for lib in library.get_combined_library_metadata()
        ]

        self.assertEqual(
            len(set(lib["scpca_project_id"] for lib in libraries_metadata)), PROJECT_COUNT
        )
        self.assertEqual(
            len(set(lib["scpca_sample_id"] for lib in libraries_metadata)), SAMPLES_COUNT
        )
        self.assertEqual(libraries.count(), LIBRARIES_COUNT)

        # Once the database is set up correctly, run the create_portal_metadata management command
        self.processor.create_portal_metadata(clean_up_output_data=False)

        # Test the content of the generated zip file here
