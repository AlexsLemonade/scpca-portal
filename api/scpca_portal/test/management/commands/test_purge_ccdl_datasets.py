from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.test.factories import ProjectFactory


class TestPurgeCCDLDatasets(TestCase):
    def setUp(self):
        self.purge_ccdl_datasets = partial(call_command, "purge_ccdl_datasets")
        self.scpca_id = "SCPCP999990"

    @patch("scpca_portal.models.CCDLDataset.purge_project_datasets", return_value=0)
    def test_purge_ccdl_datasets(self, mock_purge_project_datasets):
        self.purge_ccdl_datasets(scpca_id=self.scpca_id)
        mock_purge_project_datasets.assert_called_once_with(self.scpca_id)

    @patch("scpca_portal.models.CCDLDataset.purge_project_datasets", return_value=0)
    def test_allow_existing_project(self, mock_purge_project_datasets):
        ProjectFactory(scpca_id=self.scpca_id)

        # Should not purge datasets for a project that still exists
        self.purge_ccdl_datasets(scpca_id=self.scpca_id)
        mock_purge_project_datasets.assert_not_called()

        # Should purge them when explicitly allowed
        self.purge_ccdl_datasets(scpca_id=self.scpca_id, allow_existing_project=True)
        mock_purge_project_datasets.assert_called_once_with(self.scpca_id)
