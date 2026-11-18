from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from scpca_portal.test.factories import ProjectFactory


class TestPurgeProject(TestCase):
    def setUp(self):
        self.purge_project = partial(call_command, "purge_project")

    @patch("scpca_portal.models.Project.purge")
    def test_purge_project(self, mock_purge):
        project = ProjectFactory()
        self.purge_project(scpca_id=project.scpca_id)
        mock_purge.assert_called_once_with()

    @patch("scpca_portal.models.Project.purge")
    def test_purge_project_not_found(self, mock_purge):
        self.purge_project(scpca_id="SCPCP000000")
        mock_purge.assert_not_called()
