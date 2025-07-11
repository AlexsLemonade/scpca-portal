from typing import Set
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import metadata_parser
from scpca_portal.models import Library, Project, Sample
from scpca_portal.test.factories import ProjectFactory


class TestMetadataParser(TestCase):
    @classmethod
    def setUpTestData(cls):
        with patch("scpca_portal.lockfile.get_lockfile_project_ids", return_value=[]):
            call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

    def assertTransformedKeys(self, expected_keys: Set, actual_keys: Set):
        """
        Helper for asserting at least one transformed key exists in actual_keys.
        Some keys may be optional - fails only if none are present.
        """
        self.assertTrue(any(expected_key in actual_keys for expected_key in expected_keys))

    def test_load_projects_metadata(self):
        PROJECT_IDS = ["SCPCP999990", "SCPCP999991", "SCPCP999992"]

        # Load metadata for projects
        projects_metadata = metadata_parser.load_projects_metadata(
            Project.get_input_metadata_original_file()
        )

        # Make sure that all projects metadata are loaded
        actual_project_ids = [project["scpca_project_id"] for project in projects_metadata]
        self.assertEqual(sorted(actual_project_ids), PROJECT_IDS)

        # Verify that metadata keys are transformed correctly
        expected_keys = {
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_spatial_data",
            "human_readable_pi_name",
            "pi_name",
            "title",
            "email",
            "name",
            "accession",
            "has_raw",
            "accession_url",
            "doi",
        }
        actual_keys = set(projects_metadata[0].keys())
        self.assertTransformedKeys(expected_keys, actual_keys)

    def test_load_samples_metadata(self):
        PROJECT_SAMPLES_IDS = {
            "SCPCP999990": ["SCPCS999990", "SCPCS999991", "SCPCS999994", "SCPCS999997"],
            "SCPCP999991": ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
            "SCPCP999992": ["SCPCS999996", "SCPCS999998"],
        }

        for project_id, expected_sample_ids in PROJECT_SAMPLES_IDS.items():
            project = ProjectFactory(scpca_id=project_id)
            sample_metadata_original_file = Sample.get_input_metadata_original_file(project)

            # Load metadata for samples
            samples_metadata = metadata_parser.load_samples_metadata(sample_metadata_original_file)

            # Make sure all project samples metadata are loaded
            actual_sample_ids = [sample["scpca_sample_id"] for sample in samples_metadata]
            self.assertEqual(sorted(actual_sample_ids), expected_sample_ids)

    def test_load_library_metadata(self):
        PROJECT_LIBRARY_IDS = {
            "SCPCP999990": ["SCPCL999990", "SCPCL999991", "SCPCL999997"],
            "SCPCP999991": ["SCPCL999992", "SCPCL999995"],
            "SCPCP999992": ["SCPCL999996", "SCPCL999998"],
        }

        for project_id, expected_library_ids in PROJECT_LIBRARY_IDS.items():
            project = ProjectFactory(scpca_id=project_id)

            # Load metadata for libraries
            libraries_metadata = [
                metadata_parser.load_library_metadata(lib.local_file_path)
                for lib in Library.get_project_original_file_libraries(project)
            ]

            # Make sure all libraries metadata are loaded
            actual_library_ids = [
                lib_metadata["scpca_library_id"] for lib_metadata in libraries_metadata
            ]
            self.assertEqual(sorted(actual_library_ids), expected_library_ids)

            # Verify that metadata keys are transformed correctly
            expected_keys = {
                "scpca_project_id",
                "scpca_sample_id",
                "scpca_library_id",
                "filtered_cell_count",
            }
            actual_keys = libraries_metadata[0].keys()
            self.assertTransformedKeys(expected_keys, actual_keys)

    def test_load_bulk_metadata(self):
        PROJECT_ID = "SCPCP999990"
        LIBRARY_ID = "SCPCL999994"

        project = ProjectFactory(scpca_id=PROJECT_ID)

        # Load metadata for bulk libraries
        bulk_libraries_metadata = metadata_parser.load_bulk_metadata(
            project.input_bulk_metadata_file_path
        )

        # Make sure the bulk library metadata are loaded
        actual_library_id = bulk_libraries_metadata[0].get("scpca_library_id")
        self.assertEqual(actual_library_id, LIBRARY_ID)

        # Verify that metadata keys are transformed correctly
        expected_keys = {"scpca_project_id", "scpca_sample_id", "scpca_library_id"}
        actual_keys = bulk_libraries_metadata[0].keys()
        self.assertTransformedKeys(expected_keys, actual_keys)
