from unittest.mock import MagicMock, Mock

from django.test import TestCase

from scpca_portal.models import Library, Project


class TestGetProjectLibrariesFromDownloadConfig(TestCase):
    def setUp(self):
        self.project = Mock(spec=Project)
        self.library1 = Mock(spec=Library, modality="SINGLE_CELL", is_multiplexed=False)
        self.library2 = Mock(spec=Library, modality="SINGLE_CELL", is_multiplexed=True)
        self.library3 = Mock(spec=Library, modality="SPATIAL")
        self.empty_queryset = Library.objects.none()

        self.project.libraries.filter.return_value = self.empty_queryset | {
            self.library1,
            self.library2,
        }
        self.project.libraries.all.return_value = self.empty_queryset | {
            self.library1,
            self.library2,
            self.library3,
        }
        self.project.libraries.none.return_value = self.empty_queryset

        self.default_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }

    def setUpExcludeMultiplexedLibraries(self):
        # Use MagicMack to adequately mock the chaining property of querysets
        self.mock_queryset = MagicMock()
        self.project.libraries.filter.return_value = self.mock_queryset
        self.mock_queryset.exclude.return_value = self.empty_queryset | {self.library1}

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
        self.setUpExcludeMultiplexedLibraries()
        config = self.default_config.copy()
        config["excludes_multiplexed"] = True

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)
        self.assertNotIn(self.library2, result)

    def test_get_project_libraries_from_download_config_includes_merged_merged_file_exists(self):
        self.setUpExcludeMultiplexedLibraries()
        config = self.default_config.copy()
        config["includes_merged"] = True
        config["excludes_multiplexed"] = True
        self.project.includes_merged_sce = True

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertIn(self.library1, result)

    def test_get_project_libraries_from_download_config_includes_merged_no_merged_file(self):
        self.setUpExcludeMultiplexedLibraries()
        config = self.default_config.copy()
        config["includes_merged"] = True
        config["excludes_multiplexed"] = True
        self.project.includes_merged_sce = False
        self.project.includes_merged_anndata = False

        result = Library.get_project_libraries_from_download_config(self.project, config)
        self.assertEqual(result, self.empty_queryset)

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
        self.sample = Mock(spec=Project)
        self.library1 = Mock(spec=Library, modality="SINGLE_CELL", format="SINGLE_CELL_EXPERIMENT")
        self.library2 = Mock(spec=Library, modality="SINGLE_CELL", format="ANN_DATA")
        self.library3 = Mock(spec=Library, modality="SPATIAL", format="SINGLE_CELL_EXPERIMENT")
        self.empty_queryset = Library.objects.none()

        def filter_side_effect(*args, **kwargs):
            if kwargs == {"modality": "SINGLE_CELL", "format__contains": "SINGLE_CELL_EXPERIMENT"}:
                return self.empty_queryset | {self.library1}
            elif kwargs == {"modality": "SINGLE_CELL", "format__contains": "ANN_DATA"}:
                return self.empty_queryset | {self.library2}
            elif kwargs == {"modality": "SPATIAL", "format__contains": "SINGLE_CELL_EXPERIMENT"}:
                return self.empty_queryset | {self.library3}
            return self.empty_queryset

        self.sample.libraries.filter.side_effect = filter_side_effect

    def test_get_sample_libraries_from_download_config_single_cell_sce(self):
        config = {"modality": "SINGLE_CELL", "format": "SINGLE_CELL_EXPERIMENT"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertEqual(result, self.empty_queryset | {self.library1})

    def test_get_sample_libraries_from_download_config_single_cell_anndata(self):
        config = {"modality": "SINGLE_CELL", "format": "ANN_DATA"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertEqual(result, self.empty_queryset | {self.library2})

    def test_get_sample_libraries_from_download_config_spatial_sce(self):
        config = {"modality": "SPATIAL", "format": "SINGLE_CELL_EXPERIMENT"}
        result = Library.get_sample_libraries_from_download_config(self.sample, config)
        self.assertEqual(result, self.empty_queryset | {self.library3})

    def test_get_sample_libraries_from_download_config_invalid_configuration(self):
        invalid_config = {"modality": None, "format": None}
        with self.assertRaises(ValueError):
            Library.get_sample_libraries_from_download_config(self.sample, invalid_config)
