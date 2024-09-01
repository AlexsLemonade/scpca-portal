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

    def test_project_generate_computed_files_(self):
        pass

    def test_sample_generate_computed_files_(self):
        pass
