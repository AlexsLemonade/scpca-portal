import shutil

from django.test import TransactionTestCase

from scpca_portal import common


class TestGenerateComputedFiles(TransactionTestCase):
    def setUp(self):
        pass

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def test_create_project_SCPCP999990(self):
        pass

    def test_create_project_SCPCP999991(self):
        pass

    def test_create_project_SCPCP999992(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA_MERGED(self):
        pass

    def test_project_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_project_generate_computed_files_ALL_METADATA(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_sample_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass
