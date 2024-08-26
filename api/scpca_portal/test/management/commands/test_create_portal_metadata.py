import shutil
from zipfile import ZipFile

from django.conf import settings
from django.test import TransactionTestCase

from scpca_portal import common, readme_file
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import Library, Project, Sample

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.


class TestCreatePortalMetadata(TransactionTestCase):
    def setUp(self):
        self.processor = create_portal_metadata.Command()
        self.loader = load_data.Command()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def assertProjectReadmeContains(self, text, zip_file):
        self.assertIn(text, zip_file.read("README.md").decode("utf-8"))

    def load_test_data(self):
        # Expected object counts
        PROJECTS_COUNT = 3
        SAMPLES_COUNT = 9
        LIBRARIES_COUNT = 7

        self.loader.load_data(
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id="",
            update_s3=False,
            submitter_whitelist="scpca",
        )

        self.assertEqual(Project.objects.all().count(), PROJECTS_COUNT)
        self.assertEqual(Sample.objects.all().count(), SAMPLES_COUNT)
        self.assertEqual(Library.objects.all().count(), LIBRARIES_COUNT)

    def test_create_portal_metadata(self):
        self.load_test_data()
        self.processor.create_portal_metadata(clean_up_output_data=False)

        with ZipFile(common.OUTPUT_PORTAL_METADATA_ZIP_FILE_PATH) as zip:
            # Test the content of the generated zip file
            # There is 1 file:
            # ├── README.md
            expected_file_count = 1
            # The filenames should match the following constants specified for the computed file
            expected_file = readme_file.OUTPUT_NAME
            files = set(zip.namelist())
            self.assertEqual(len(files), expected_file_count)
            self.assertIn(expected_file, files)

            # Test the content of README.md
            expected_text = (
                "This download includes associated metadata for samples from all projects"
            )
            self.assertProjectReadmeContains(expected_text, zip)
