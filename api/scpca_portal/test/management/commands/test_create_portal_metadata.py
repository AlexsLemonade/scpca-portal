import shutil
from zipfile import ZipFile

from django.test import TransactionTestCase

from scpca_portal import common, readme_file
from scpca_portal.management.commands import create_portal_metadata, load_data
from scpca_portal.models import ComputedFile, Library

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

    def assertProjectReadmeContains(self, text, zip_file):
        self.assertIn(text, zip_file.read("README.md").decode("utf-8"))

    def load_test_data(self):
        # Load the test data and make sure the database is set up correctly
        PROJECT_COUNT = 3
        SAMPLES_COUNT = 8
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

    def test_zip_file(self):
        # Test the content of the generated zip file here
        # There are 2 files:
        # ├── README.md
        # |── metadata.tsv
        expected_file_count = 2
        # The filenames should match the following constants specified for the computed file
        expected_files = {
            readme_file.OUTPUT_NAME,
            ComputedFile.MetadataFilenames.METADATA_ONLY_FILE_NAME,
        }

        with ZipFile(common.OUTPUT_PORTAL_METADATA_ZIP_FILE_PATH) as zip:
            files = set(zip.namelist())
            self.assertEqual(len(files), expected_file_count)
            self.assertEqual(files, expected_files)
            for expected_file in expected_files:
                self.assertIn(expected_file, files)

    def test_readme_file(self):
        # Test the content of README.md here
        expected_text = "The metadata included in this download contains"

        with ZipFile(common.OUTPUT_PORTAL_METADATA_ZIP_FILE_PATH) as zip:
            self.assertProjectReadmeContains(expected_text, zip)

    def test_metadata_file(self):
        # Test the content of metadata.tsv here
        expected_row_count = 9  # Header + 8 records
        expected_keys = [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter_id",
            "organism",
            "development_stage_ontology_term_id",
            "sex_ontology_term_id",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "disease_ontology_term_id",
            "tissue_ontology_term_id",
            "seq_unit",
            "technology",
            "demux_samples",
            "total_reads",
            "mapped_reads",
            "sample_cell_count_estimate",
            "sample_cell_estimate",
            "unfiltered_cells",
            "filtered_cell_count",
            "processed_cells",
            "filtered_spots",
            "unfiltered_spots",
            "tissue_spots",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "pi_name",
            "project_title",
            "genome_assembly",
            "mapping_index",
            "spaceranger_version",
            "alevin_fry_version",
            "salmon_version",
            "transcript_type",
            "droplet_filtering_method",
            "cell_filtering_method",
            "prob_compromised_cutoff",
            "min_gene_cutoff",
            "normalization_method",
            "demux_method",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
        ]

        with ZipFile(common.OUTPUT_PORTAL_METADATA_ZIP_FILE_PATH) as zip:
            content = [
                row
                for row in zip.read(ComputedFile.MetadataFilenames.METADATA_ONLY_FILE_NAME)
                .decode("utf-8")
                .split("\r\n")
                if row
            ]

            self.assertEqual(len(content), expected_row_count)
            self.assertEqual(content[0].split(common.TAB), expected_keys)

    def test_create_portal_metadata(self):
        self.load_test_data()
        self.processor.create_portal_metadata(clean_up_output_data=False)
        self.test_zip_file()
        self.test_readme_file()
        self.test_metadata_file()
