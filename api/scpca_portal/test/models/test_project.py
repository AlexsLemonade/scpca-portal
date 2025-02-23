from django.test import TestCase

from scpca_portal import common
from scpca_portal.enums import Modalities
from scpca_portal.test.factories import LibraryFactory, ProjectFactory


class TestGetLibraries(TestCase):
    def setUp(self):
        self.project = ProjectFactory(has_multiplexed_data=True)
        self.library_single_cell_no_multiplexed = LibraryFactory(
            project=self.project, modality=Modalities.SINGLE_CELL, is_multiplexed=False
        )
        self.library_single_cell_multiplexed = LibraryFactory(
            project=self.project, modality=Modalities.SINGLE_CELL, is_multiplexed=True
        )
        self.library_spatial = LibraryFactory(project=self.project, modality=Modalities.SPATIAL)

    def test_get_libraries_valid_config(self):
        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]

        result = self.project.get_libraries(download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)

    def test_get_libraries_invalid_config(self):
        download_config = {
            "modality": None,
            "format": None,
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        with self.assertRaises(ValueError):
            self.project.get_libraries(download_config)

    def test_get_libraries_empty_config(self):
        download_config = {}
        result = self.project.get_libraries(download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)
        self.assertIn(self.library_spatial, result)

    def test_get_libraries_no_config_passed(self):
        result = self.project.get_libraries()
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)
        self.assertIn(self.library_spatial, result)

    def test_get_libraries_metadata_only(self):
        download_config_name = "ALL_METADATA"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]

        result = self.project.get_libraries(download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)
        self.assertIn(self.library_spatial, result)

    def test_get_libraries_excludes_multiplexed(self):
        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]

        result = self.project.get_libraries(download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertNotIn(self.library_single_cell_multiplexed, result)

    def test_get_libraries_includes_merged_merged_file_exists(self):
        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        self.project.includes_merged_sce = True

        result = self.project.get_libraries(download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)

    def test_get_libraries_includes_merged_no_merged_file(self):
        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        self.project.includes_merged_sce = False
        self.project.includes_merged_anndata = False

        result = self.project.get_libraries(download_config)
        self.assertFalse(result.exists())
