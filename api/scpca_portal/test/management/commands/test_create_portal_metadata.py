import csv
import shutil
from io import TextIOWrapper
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import ComputedFile, Library, Project, Sample

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.


README_FILE = readme_file.OUTPUT_NAME
METADATA_FILE = metadata_file.MetadataFilenames.METADATA_ONLY_FILE_NAME


class TestCreatePortalMetadata(TransactionTestCase):
    def setUp(self):
        self.processor = create_portal_metadata.Command()
        self.loader = load_data.Command()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

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

    # TODO: After PR #839 is merged into dev, add readme file format testing
    def assertProjectReadmeContains(self, text, zip_file):
        self.assertIn(text, zip_file.read(README_FILE).decode("utf-8"))

    @patch("scpca_portal.management.commands.create_portal_metadata.s3.upload_output_file")
    def test_create_portal_metadata(self, mock_upload_output_file):
        # Set up the database for test
        self.load_test_data()
        # Create the portal metadata computed_file
        computed_file = self.processor.create_portal_metadata(
            clean_up_output_data=False, update_s3=True
        )

        # Test computed_file
        if computed_file:
            expected_size = 8469
            self.assertEqual(computed_file.size_in_bytes, expected_size)
            mock_upload_output_file.assert_called_once_with(
                computed_file.s3_key, computed_file.s3_bucket
            )
        else:
            self.fail("No computed file")

        # Test the content of the generated zip file
        zip_file_path = ComputedFile.get_local_file_path(
            common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG
        )
        with ZipFile(zip_file_path) as zip_file:
            # There are 2 file:
            # ├── README.md
            # |── metadata.tsv
            expected_file_count = 2
            # Make sure the zip has the exact number of expected files
            files = set(zip_file.namelist())
            self.assertEqual(len(files), expected_file_count)
            self.assertIn(README_FILE, files)
            self.assertIn(METADATA_FILE, files)
            # README.md
            expected_text = (
                "This download includes associated metadata for samples from all projects"
            )
            self.assertProjectReadmeContains(expected_text, zip_file)
            # metadata.tsv
            with zip_file.open(METADATA_FILE) as metadata_file:
                csv_reader = csv.DictReader(
                    TextIOWrapper(metadata_file, "utf-8"),
                    delimiter=common.TAB,
                )
                rows = list(csv_reader)
                column_headers = list(rows[0].keys())
                # Make sure the number of rows matches the expected count (excludes the header)
                expected_row_count = 8  # 8 records - 1 header
                self.assertEqual(len(rows), expected_row_count)
                # Make sure the header keys match the common sort order list (excludes '*')
                expected_keys = set(common.METADATA_COLUMN_SORT_ORDER) - set(["*"])
                output_keys = set(column_headers)
                self.assertEqual(output_keys, expected_keys)
                # Make sure all library Ids are present
                expected_libraries = set(Library.objects.all().values_list("scpca_id", flat=True))
                output_libraries = set(
                    [row[common.LIBRARY_ID_KEY] for row in rows if common.LIBRARY_ID_KEY in row]
                )
                self.assertEquals(output_libraries, expected_libraries)

    @patch("scpca_portal.management.commands.create_portal_metadata.s3.delete_output_file")
    def test_only_one_computed_file_at_any_point(self, mock_delete_output_file):
        # Set up the database for test
        self.load_test_data()
        # First call to create the portal metadata computed file
        computed_file_one = self.processor.create_portal_metadata(
            clean_up_output_data=False, update_s3=True
        )
        # Second call to create the portal metadata computed file
        self.processor.create_portal_metadata(clean_up_output_data=False, update_s3=True)
        mock_delete_output_file.assert_called_with(
            computed_file_one.s3_key, computed_file_one.s3_bucket
        )
        # Make sure pre-existing computed_file has been deleted and only one exists
        existing_computed_file = ComputedFile.objects.filter(portal_metadata_only=True)
        self.assertEqual(existing_computed_file.count(), 1)
