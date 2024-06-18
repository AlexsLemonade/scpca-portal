from django.test import TestCase

from scpca_portal.models import Library
from scpca_portal.test.factories import LibraryFactory, ProjectFactory, SampleFactory


class TestGetProjectLibrariesFromDownloadConfig(TestCase):
    def setUp(self):
        self.project = ProjectFactory()
        self.library1 = LibraryFactory(
            project=self.project, modality=Library.Modalities.SINGLE_CELL, is_multiplexed=False
        )
        self.library2 = LibraryFactory(
            project=self.project, modality=Library.Modalities.SINGLE_CELL, is_multiplexed=True
        )
        self.library3 = LibraryFactory(project=self.project, modality=Library.Modalities.SPATIAL)

        self.default_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }

    def test_get_project_libraries_from_download_config_valid_config(self):
        config = self.default_config
        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)
        self.assertIn(self.library2, result)

    def test_get_project_libraries_from_download_config_invalid_config(self):
        config = self.default_config.copy()
        config["modality"] = None
        with self.assertRaises(ValueError):
            Library.get_project_libraries_from_download_config(self.project, config)

    def test_get_project_libraries_from_download_config_excludes_multiplexed(self):
        config = self.default_config.copy()
        config["excludes_multiplexed"] = True

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)
        self.assertNotIn(self.library2, result)

    def test_get_project_libraries_from_download_config_includes_merged_merged_file_exists(self):
        config = self.default_config.copy()
        config["includes_merged"] = True
        config["excludes_multiplexed"] = True
        self.project.includes_merged_sce = True

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)

    def test_get_project_libraries_from_download_config_includes_merged_no_merged_file(self):
        config = self.default_config.copy()
        config["includes_merged"] = True
        config["excludes_multiplexed"] = True
        self.project.includes_merged_sce = False
        self.project.includes_merged_anndata = False

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertEqual(result.count(), 0)

    def test_get_project_libraries_from_download_config_metadata_only(self):
        config = {
            "modality": None,
            "format": None,
            "excludes_multiplexed": None,
            "includes_merged": None,
            "metadata_only": True,
        }
        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)
        self.assertIn(self.library2, result)
        self.assertIn(self.library3, result)


class TestGetSampleLibrariesFromDownloadConfig(TestCase):
    def setUp(self):
        self.sample = SampleFactory()
        self.library1 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT, Library.FileFormats.ANN_DATA],
        )
        self.library2 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT],
        )
        self.library3 = LibraryFactory(
            modality=Library.Modalities.SINGLE_CELL, formats=[Library.FileFormats.ANN_DATA]
        )
        self.library4 = LibraryFactory(
            modality=Library.Modalities.SPATIAL,
            formats=[Library.FileFormats.SINGLE_CELL_EXPERIMENT],
        )
        self.sample.libraries.add(self.library1, self.library2, self.library3, self.library4)

    def test_get_sample_libraries_from_download_config_single_cell_sce(self):
        config = {"modality": "SINGLE_CELL", "format": "SINGLE_CELL_EXPERIMENT"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertIn(self.library1, result)
        self.assertIn(self.library2, result)

    def test_get_sample_libraries_from_download_config_single_cell_anndata(self):
        config = {"modality": "SINGLE_CELL", "format": "ANN_DATA"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertIn(self.library1, result)
        self.assertIn(self.library3, result)

    def test_get_sample_libraries_from_download_config_spatial_sce(self):
        config = {"modality": "SPATIAL", "format": "SINGLE_CELL_EXPERIMENT"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertIn(self.library4, result)

    def test_get_sample_libraries_from_download_config_invalid_configuration(self):
        invalid_config = {"modality": None, "format": None}
        with self.assertRaises(ValueError):
            Library.get_sample_libraries_from_download_config(self.sample, invalid_config)
