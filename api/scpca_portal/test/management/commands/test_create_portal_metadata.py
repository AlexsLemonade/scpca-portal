import csv
import shutil
from io import TextIOWrapper
from typing import Dict
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import ComputedFile, Library, Project, Sample

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.

ALLOWED_SUBMITTERS = {"scpca"}


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
            allowed_submitters=list(ALLOWED_SUBMITTERS),
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )

        self.assertEqual(Project.objects.all().count(), PROJECTS_COUNT)
        self.assertEqual(Sample.objects.all().count(), SAMPLES_COUNT)
        self.assertEqual(Library.objects.all().count(), LIBRARIES_COUNT)

    # TODO: After PR #839 is merged into dev, add readme file format testing
    def assertProjectReadmeContains(self, text, zip_file):
        self.assertIn(text, zip_file.read(README_FILE).decode("utf-8"))

    def assertFields(self, computed_file, expected_fields: Dict):
        for expected_key, expected_value in expected_fields.items():
            actual_value = getattr(computed_file, expected_key)
            message = f"Expected {expected_value}, received {actual_value} on '{expected_key}'"
            self.assertEqual(actual_value, expected_value, message)

    def assertEqualWithVariance(self, value, expected, variance=50):
        # Make sure the given value is within the range of expected bounds
        message = f"{value} is out of range"
        self.assertGreaterEqual(value, expected - variance, message)
        self.assertLessEqual(value, expected + variance, message)

    @patch("scpca_portal.management.commands.create_portal_metadata.s3.upload_output_file")
    def test_create_portal_metadata(self, mock_upload_output_file):
        # Set up the database for test
        self.load_test_data()
        # Create the portal metadata computed file
        self.processor.create_portal_metadata(clean_up_output_data=False, update_s3=True)

        # Test the computed file
        computed_files = ComputedFile.objects.filter(portal_metadata_only=True)
        # Make sure the computed file is created and singular
        self.assertEqual(computed_files.count(), 1)
        computed_file = computed_files.first()
        # Make sure the computed file size is as expected range
        self.assertEqualWithVariance(computed_file.size_in_bytes, 8430)
        # Make sure all fields match the download configuration values
        download_config = {
            "modality": None,
            "format": None,
            "includes_merged": False,
            "metadata_only": True,
            "portal_metadata_only": True,
        }
        self.assertFields(computed_file, download_config)
        # Make sure mock_upload_output_file called once
        mock_upload_output_file.assert_called_once_with(
            computed_file.s3_key, computed_file.s3_bucket
        )

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
