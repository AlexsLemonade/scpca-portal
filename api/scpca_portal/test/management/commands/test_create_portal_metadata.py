import csv
import re
import shutil
from functools import partial
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file, utils
from scpca_portal.models import ComputedFile, Library, Project, Sample

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.

README_DIR = common.DATA_PATH / "readmes"
README_FILE = readme_file.OUTPUT_NAME
METADATA_FILE = metadata_file.MetadataFilenames.METADATA_ONLY_FILE_NAME


class TestCreatePortalMetadata(TransactionTestCase):
    def setUp(self):
        self.create_portal_metadata = partial(call_command, "create_portal_metadata")
        self.load_data = partial(call_command, "load_data")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def load_test_data(self):
        # Expected object counts
        PROJECTS_COUNT = 3
        SAMPLES_COUNT = 9
        LIBRARIES_COUNT = 7

        self.load_data(
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_existing=False,
            scpca_project_id="",
            update_s3=False,
            submitter_whitelist="scpca",
        )

        self.assertEqual(Project.objects.all().count(), PROJECTS_COUNT)
        self.assertEqual(Sample.objects.all().count(), SAMPLES_COUNT)
        self.assertEqual(Library.objects.all().count(), LIBRARIES_COUNT)

    def assertProjectReadmeContent(self, zip_file, project_ids: List[str]) -> None:
        def get_updated_content(content: str) -> str:
            """
            Replace the placeholders PROJECT_ID_{i} and TEST_TODAYS_DATE in test_data/readmes
            with the given project_id and today's date respectively for format testing."
            """
            content = content.replace(
                "Generated on: TEST_TODAYS_DATE", f"Generated on: {utils.get_today_string()}"
            )
            # Map project_ids to their coressponding placeholders with indecies in readmes
            for i, project_id in enumerate(project_ids):
                content = content.replace(f"PROJECT_ID_{i}", project_id)

            return content.strip()

        # Get the corresponding saved readme output path based on the zip filename
        readme_filename = re.sub(r"^[A-Z]{5}\d{6}_", "", Path(zip_file.filename).stem) + ".md"
        saved_readme_output_path = README_DIR / readme_filename
        # Convert expected and output contents to line lists for easier debugging
        with zip_file.open(README_FILE) as readme_file:
            output_content = readme_file.read().decode("utf-8").splitlines(True)
        with saved_readme_output_path.open("r", encoding="utf-8") as saved_readme_file:
            expected_content = get_updated_content(saved_readme_file.read()).splitlines(True)
        self.assertEqual(
            expected_content,
            output_content,
            f"{self._testMethodName}: Comparison with {readme_filename} does not match.",
        )

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
        self.create_portal_metadata(clean_up_output_data=False, update_s3=True)

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
            self.assertProjectReadmeContent(
                zip_file, list(Project.objects.values_list("scpca_id", flat=True).distinct())
            )
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
