import shutil
from functools import partial

from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import common


class TestGenerateComputedFiles(TransactionTestCase):
    def setUp(self):
        self.load_metadata = partial(call_command, "load_metadata")
        self.generate_computed_files = partial(call_command, "generate_computed_files")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def test_project_SCPCP999990(self):
        pass

    def test_project_SCPCP999991(self):
        pass

    def test_project_SCPCP999992(self):
        pass

    def test_clean_up_input_data(self):
        pass

    def test_clean_up_output_data(self):
        pass

    def test_custom_max_workers(self):
        pass

    def test_passed_scpca_project_id(self):
        pass

    def test_update_s3(self):
        pass
