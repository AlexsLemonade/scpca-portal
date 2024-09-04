import csv
import shutil
from io import TextIOWrapper
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

    def assertProjectReadmeContains(self, text, zip_file):
        self.assertIn(text, zip_file.read("README.md").decode("utf-8"))

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

    def test_create_portal_metadata(self):
        self.load_test_data()
        self.processor.create_portal_metadata(clean_up_output_data=False)

        zip_file_path = ComputedFile.get_local_file_path(
            common.GENERATED_PORTAL_METADATA_DOWNLOAD_CONFIG
        )
        with ZipFile(zip_file_path) as zip:
            # Test the content of the generated zip file
            # There are 2 file:
            # ├── README.md
            # |── metadata.tsv
            expected_file_count = 2
            # Make sure the zip has the exact number of expected files
            files = set(zip.namelist())
            self.assertEqual(len(files), expected_file_count)
            self.assertIn(README_FILE, files)
            self.assertIn(METADATA_FILE, files)
            # README.md
            expected_text = (
                "This download includes associated metadata for samples from all projects"
            )
            self.assertProjectReadmeContains(expected_text, zip)
            # metadata.tsv
            with zip.open(METADATA_FILE) as metadata_file:
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
