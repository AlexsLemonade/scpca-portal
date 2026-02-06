import csv
import shutil
from functools import partial
from io import TextIOWrapper
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file
from scpca_portal.models import ComputedFile, Library, Project, Sample

# NOTE: Test data bucket is defined in `config/test.py`.
# When settings.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.

README_FILE = readme_file.OUTPUT_NAME
METADATA_FILE = metadata_file.MetadataFilenames.METADATA_ONLY_FILE_NAME


class TestCreatePortalMetadata(TransactionTestCase):
    def setUp(self):
        # make sure OriginalFile table is populated
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        self.create_portal_metadata = partial(call_command, "create_portal_metadata")
        self.load_metadata = partial(call_command, "load_metadata")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.OUTPUT_DATA_PATH, ignore_errors=True)

    def load_test_data(self):
        # Expected object counts
        PROJECTS_COUNT = 3
        SAMPLES_COUNT = 9
        LIBRARIES_COUNT = 8

        self.load_metadata(
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            reload_existing=False,
            update_s3=False,
            submitter_whitelist="scpca",
        )

        self.assertEqual(Project.objects.all().count(), PROJECTS_COUNT)
        self.assertEqual(Sample.objects.all().count(), SAMPLES_COUNT)
        self.assertEqual(Library.objects.all().count(), LIBRARIES_COUNT)

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
        self.create_portal_metadata(clean_up_output_data=False, update_s3=True)

        # Test the computed file
        computed_files = ComputedFile.objects.filter(portal_metadata_only=True)
        # Make sure the computed file is created and singular
        self.assertEqual(computed_files.count(), 1)
        computed_file = computed_files.first()
        # Make sure the computed file size is as expected range
        self.assertEqualWithVariance(
            computed_file.size_in_bytes, 8803
        )  # TODO: add to expected_values portal wide dataset file
        # Make sure all the fields have correct values
        self.assertTrue(computed_file.metadata_only)
        self.assertTrue(computed_file.portal_metadata_only)
        self.assertFalse(computed_file.has_bulk_rna_seq)
        self.assertFalse(computed_file.has_cite_seq_data)
        self.assertFalse(computed_file.has_multiplexed_data)
        self.assertFalse(computed_file.includes_merged)
        self.assertIsNone(computed_file.format)
        self.assertIsNone(computed_file.modality)
        self.assertIsNone(computed_file.project)
        self.assertIsNone(computed_file.sample)

        # Make sure mock_upload_output_file called once
        mock_upload_output_file.assert_called_once_with(
            computed_file.s3_key, computed_file.s3_bucket
        )

        # Test the content of the generated zip file
        zip_file_path = ComputedFile.get_local_file_path(common.PORTAL_METADATA_DOWNLOAD_CONFIG)
        with ZipFile(zip_file_path) as zip_file:
            # There are 2 file:
            # ├── README.md
            # |── metadata.tsv
            expected_file_count = 2
            # Make sure the zip has the exact number of expected files
            files = set(zip_file.namelist())
            self.assertEqual(len(files), expected_file_count)
            # Make sure all expected files are included
            self.assertIn(README_FILE, files)
            self.assertIn(METADATA_FILE, files)
            # Test metadata.tsv
            with zip_file.open(METADATA_FILE) as metadata_file:
                csv_reader = csv.DictReader(
                    TextIOWrapper(metadata_file, "utf-8"),
                    delimiter=common.TAB,
                )
                rows = list(csv_reader)
                column_headers = list(rows[0].keys())
                # Make sure the number of rows matches the expected count (excludes the header)
                expected_row_count = 9  # 9 records - 1 header
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
                self.assertEqual(output_libraries, expected_libraries)

    @patch("scpca_portal.management.commands.create_portal_metadata.s3.delete_output_file")
    def test_only_one_computed_file_at_any_point(self, mock_delete_output_file):
        # Set up the database for test
        self.load_test_data()
        # Make sure pre-existing computed_file has been deleted and only one exists
        self.create_portal_metadata(clean_up_output_data=False, update_s3=True)
        self.create_portal_metadata(clean_up_output_data=False, update_s3=True)
        computed_files = ComputedFile.objects.filter(portal_metadata_only=True)
        self.assertEqual(computed_files.count(), 1)
        # Make sure mock_delete_output_file can be called with computed_file field values
        computed_file = computed_files.first()
        mock_delete_output_file.assert_called_once_with(
            computed_file.s3_key, computed_file.s3_bucket
        )
