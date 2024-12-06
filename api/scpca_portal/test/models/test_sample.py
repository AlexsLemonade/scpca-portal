from django.test import TestCase

from scpca_portal import common
from scpca_portal.models import Library
from scpca_portal.test.factories import LibraryFactory, SampleFactory


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

        self.library_list = [library1, library2, library3, library4]

    def test_get_libraries_all_configs(self):
        for config in common.SAMPLE_DOWNLOAD_CONFIGS.values():
            result = self.sample.get_libraries(config)
            for library in self.libraries.get(config["modality"]).get(config["format"]):
                self.assertIn(library, result)

    def test_get_libraries_invalid_configuration(self):
        invalid_config = {"modality": None, "format": None}
        with self.assertRaises(ValueError):
            self.sample.get_libraries(invalid_config)

    def test_get_libraries_empty_config(self):
        download_config = {}
        result = self.sample.get_libraries(download_config)
        for library in self.library_list:
            self.assertIn(library, result)

    def test_get_libraries_no_config_passed(self):
        result = self.sample.get_libraries()
        for library in self.library_list:
            self.assertIn(library, result)
