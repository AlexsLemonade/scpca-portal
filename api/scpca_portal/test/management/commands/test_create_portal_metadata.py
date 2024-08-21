import csv
import shutil
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file
from scpca_portal.models import ComputedFile, Library, Project, Sample

from scpca_portal.management.commands import create_portal_metadata  # isort:skip
from scpca_portal.management.commands import configure_aws_cli  # isort:skip
from scpca_portal.management.commands import load_data  # isort:skip

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
        configure_aws_cli.Command()  # TEMP Prevent load_data test from running in parallel

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
            allowed_submitters=ALLOWED_SUBMITTERS,
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
            mock_upload_output_file.assert_called_once_with(computed_file.s3_key)
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
            # The filenames should match the following constants
            expected_files = {
                README_FILE,
                METADATA_FILE,
            }
            files = set(zip_file.namelist())
            self.assertEqual(len(files), expected_file_count)
            self.assertEqual(files, expected_files)
            for expected_file in expected_files:
                self.assertIn(expected_file, files)

            # README.md
            expected_text = (
                "This download includes associated metadata for samples from all projects"
            )
            self.assertProjectReadmeContains(expected_text, zip_file)

            # metadata.tsv
            tsv = zip_file.read(METADATA_FILE).decode("utf-8").splitlines()
            rows = list(csv.DictReader(tsv, delimiter=common.TAB))
            # The header keys should match the common sort order list (excludes '*')
            expected_keys = list(filter(lambda k: k != "*", common.METADATA_COLUMN_SORT_ORDER))
            expected_row_count = 8  # 8 records (excludes the header)
            self.assertEqual(list(rows[0].keys()), expected_keys)
            self.assertEqual(len(rows), expected_row_count)

    @patch("scpca_portal.management.commands.create_portal_metadata.s3.delete_output_file")
    def test_purge_computed_file(self, mock_delete_output_file):
        # Set up the database for test
        self.load_test_data()
        # Create the portal metadata computed_file to purge
        computed_file = self.processor.create_portal_metadata(clean_up_output_data=False)

        if computed_file:
            computed_file_before_purge = ComputedFile.objects.filter(
                id=computed_file.id, portal_metadata_only=True
            ).first()
            # Purge computed_file
            self.processor.purge_computed_file(delete_from_s3=True)
            mock_delete_output_file.assert_called_once_with(computed_file.s3_key)
            # Make sure that computed_file with matching id has been deleted
            computed_file_after_purge = ComputedFile.objects.filter(
                id=computed_file_before_purge.id, portal_metadata_only=True
            ).first()
            self.assertIsNone(computed_file_after_purge)
        else:
            self.fail("No computed file to purge")
