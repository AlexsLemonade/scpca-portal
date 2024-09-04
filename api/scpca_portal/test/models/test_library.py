from django.test import TestCase

from scpca_portal import common
from scpca_portal.models import Library
from scpca_portal.test.factories import LibraryFactory, ProjectFactory, SampleFactory


class TestGetProjectLibrariesFromDownloadConfig(TestCase):
    def setUp(self):
        self.project = ProjectFactory(has_multiplexed_data=True)
        self.library_single_cell_no_multiplexed = LibraryFactory(
            project=self.project, modality=Library.Modalities.SINGLE_CELL, is_multiplexed=False
        )
        self.library_single_cell_multiplexed = LibraryFactory(
            project=self.project, modality=Library.Modalities.SINGLE_CELL, is_multiplexed=True
        )
        self.library_spatial = LibraryFactory(
            project=self.project, modality=Library.Modalities.SPATIAL
        )

    def test_get_project_libraries_from_download_config_valid_config(self):
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        result = Library.get_project_libraries_from_download_config(self.project, download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)

    def test_get_project_libraries_from_download_config_invalid_config(self):
        download_config = {
            "modality": None,
            "format": None,
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        with self.assertRaises(ValueError):
            Library.get_project_libraries_from_download_config(self.project, download_config)

    def test_get_project_libraries_from_download_config_excludes_multiplexed(self):
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": False,
            "metadata_only": False,
        }
        result = Library.get_project_libraries_from_download_config(self.project, download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertNotIn(self.library_single_cell_multiplexed, result)

    def test_get_project_libraries_from_download_config_includes_merged_merged_file_exists(self):
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        self.project.includes_merged_sce = True

        result = Library.get_project_libraries_from_download_config(self.project, download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)

    def test_get_project_libraries_from_download_config_includes_merged_no_merged_file(self):
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        self.project.includes_merged_sce = False
        self.project.includes_merged_anndata = False

        result = Library.get_project_libraries_from_download_config(self.project, download_config)
        self.assertFalse(result.exists())

    def test_get_project_libraries_from_download_config_metadata_only(self):
        download_config = {
            "modality": None,
            "format": None,
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": True,
        }
        result = Library.get_project_libraries_from_download_config(self.project, download_config)
        self.assertIn(self.library_single_cell_no_multiplexed, result)
        self.assertIn(self.library_single_cell_multiplexed, result)
        self.assertIn(self.library_spatial, result)


class TestGetSampleLibrariesFromDownloadConfig(TestCase):
    def setUp(self):
        self.sample = SampleFactory()

        library1 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT, Library.FileFormats.ANN_DATA],
        )
        library2 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT],
        )
        library3 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL, formats=[Library.FileFormats.ANN_DATA]
        )
        library4 = LibraryFactory(
            modality=Library.Modalities.SPATIAL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT],
        )
        self.sample.libraries.add(library1, library2, library3, library4)

        self.libraries = {
            "SINGLE_CELL": {
                "SINGLE_CELL_EXPERIMENT": [library1, library2],
                "ANN_DATA": [library1, library3],
            },
            "SPATIAL": {"SINGLE_CELL_EXPERIMENT": [library4]},
        }

    def test_get_sample_libraries_from_download_config_all_configs(self):
        for config in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGS:
            result = Library.get_sample_libraries_from_download_config(self.sample, config)
            for library in self.libraries.get(config["modality"]).get(config["format"]):
                self.assertIn(library, result)

    def test_get_sample_libraries_from_download_config_invalid_configuration(self):
        invalid_config = {"modality": None, "format": None}
        with self.assertRaises(ValueError):
            Library.get_sample_libraries_from_download_config(self.sample, invalid_config)
